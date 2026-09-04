`timescale 1ps/1ps

module tb_golay_decoder_exhaustive();

    localparam int CODEWORD_COUNT = 4096;
    localparam int ERROR_COUNT = 12951;

    localparam int PIPELINE_LATENCY = 3;
    localparam logic [23 : 0] TEST_CODEWORD = 24'hA5C9A5;
    localparam string CODEWORDS_FILE = "/home/dlugano/Fulgor/FEC_2026/TP2/vectors/golay_codewords.hex";
    localparam string ERRORS_FILE = "/home/dlugano/Fulgor/FEC_2026/TP2/vectors/golay_errors_w0_w4.hex";
    parameter time CLK_PERIOD = 5ns; //! 200 MHz

    logic          i_clk;
    logic          i_rst;
    logic [23 : 0] i_rx;
    logic [23 : 0] o_cw;
    logic [11 : 0] o_msg;
    logic [23 : 0] o_err;
    logic          o_corrected;
    logic          o_uncorrectable;

    logic [23 : 0] codewords [0 : CODEWORD_COUNT-1];
    logic [23 : 0] errors [0 : ERROR_COUNT-1];

    logic [23 : 0] expected_cw [0 : PIPELINE_LATENCY-1];
    logic [11 : 0] expected_msg [0 : PIPELINE_LATENCY-1];
    logic [23 : 0] expected_err [0 : PIPELINE_LATENCY-1];
    logic          expected_corrected [0 : PIPELINE_LATENCY-1];
    logic          expected_uncorrectable [0 : PIPELINE_LATENCY-1];
    logic          expected_valid [0 : PIPELINE_LATENCY-1];

    int error_count;
    int checked_count;

    initial i_clk = 0;
    always #(CLK_PERIOD/2) i_clk = ~i_clk;

    golay_decoder
    u_golay_decoder (
        .i_clk(i_clk),
        .i_rst(i_rst),
        .i_rx(i_rx),
        .o_cw(o_cw),
        .o_msg(o_msg),
        .o_err(o_err),
        .o_corrected(o_corrected),
        .o_uncorrectable(o_uncorrectable)
    );

    task automatic check_output();
        if (expected_valid[PIPELINE_LATENCY-1]) begin
            checked_count++;

            if (expected_uncorrectable[PIPELINE_LATENCY-1]) begin
                // Cuando o_uncorrectable=1, o_cw, o_msg y o_err no son validos, por lo que no se chequean
                if ({o_corrected, o_uncorrectable} !== 2'b01) begin
                    $error("Uncorrectable: expected flags=01 obtained=%0b%0b", o_corrected, o_uncorrectable);
                    error_count++;
                end
            end else begin
                if ({o_cw, o_msg, o_err, o_corrected, o_uncorrectable} !==
                    {expected_cw[PIPELINE_LATENCY-1],
                     expected_msg[PIPELINE_LATENCY-1],
                     expected_err[PIPELINE_LATENCY-1],
                     expected_corrected[PIPELINE_LATENCY-1],
                     expected_uncorrectable[PIPELINE_LATENCY-1]}) begin

                    $error("expected cw=%06h msg=%03h err=%06h flags=%0b%0b, obtained cw=%06h msg=%03h err=%06h flags=%0b%0b",
                            expected_cw[PIPELINE_LATENCY-1],
                            expected_msg[PIPELINE_LATENCY-1],
                            expected_err[PIPELINE_LATENCY-1],
                            expected_corrected[PIPELINE_LATENCY-1],
                            expected_uncorrectable[PIPELINE_LATENCY-1],
                            o_cw, o_msg, o_err, o_corrected, o_uncorrectable
                    );
                    error_count++;
                end
            end
        end
    endtask

    task automatic shift_pipeline();
        for (int i = PIPELINE_LATENCY-1; i > 0; i--) begin
            expected_cw[i] = expected_cw[i-1];
            expected_msg[i] = expected_msg[i-1];
            expected_err[i] = expected_err[i-1];
            expected_corrected[i] = expected_corrected[i-1];
            expected_uncorrectable[i] = expected_uncorrectable[i-1];
            expected_valid[i] = expected_valid[i-1];
        end
    endtask

    task automatic apply_vector(
        input logic [23 : 0] codeword,
        input logic [23 : 0] error,
        input logic          uncorrectable
    );
        @(negedge i_clk);

        check_output();
        shift_pipeline();

        i_rx = codeword ^ error;
        expected_cw[0] = codeword;
        expected_msg[0] = codeword[23:12];
        expected_err[0] = error;
        expected_corrected[0] = |error;
        expected_uncorrectable[0] = uncorrectable;
        expected_valid[0] = 1'b1;
    endtask

    task automatic flush_pipeline();
        for (int cycle = 0; cycle < PIPELINE_LATENCY; cycle++) begin
            @(negedge i_clk);

            check_output();
            shift_pipeline();

            i_rx = '0;
            expected_cw[0] = '0;
            expected_msg[0] = '0;
            expected_err[0] = '0;
            expected_corrected[0] = 1'b0;
            expected_uncorrectable[0] = 1'b0;
            expected_valid[0] = 1'b0;
        end
    endtask

    initial begin
        $display("");
        $display("========================================");
        $display("Testbench de golay_decoder");
        $display("========================================");
        $display("");

        error_count = 0;
        checked_count = 0;

        i_rst = 1'b1;
        i_rx = '0;
    
        for (int i = 0; i < PIPELINE_LATENCY; i++) begin
            expected_cw[i] = '0;
            expected_msg[i] = '0;
            expected_err[i] = '0;
            expected_corrected[i] = 1'b0;
            expected_uncorrectable[i] = 1'b0;
            expected_valid[i] = 1'b0;
        end

        $readmemh(CODEWORDS_FILE, codewords);
        $readmemh(ERRORS_FILE, errors);

        repeat(2) @(negedge i_clk);
        i_rst = 1'b0;

        flush_pipeline();

        $display("# Verificación de las %0d codewords", CODEWORD_COUNT);

        for (int i = 0; i < CODEWORD_COUNT; i++) begin
            apply_vector(codewords[i], 24'h000000, 1'b0);
        end

        $display("# Verificación de codeword %06h con %0d errores de peso 0 a 4", TEST_CODEWORD, ERROR_COUNT);

        for (int i = 0; i < ERROR_COUNT; i++) begin
            apply_vector(TEST_CODEWORD, errors[i], $countones(errors[i]) > 3);
        end

        flush_pipeline();

        if (checked_count !== CODEWORD_COUNT + ERROR_COUNT) begin
            $error("Cantidad verificada incorrecta: expected=%0d obtained=%0d", CODEWORD_COUNT + ERROR_COUNT, checked_count);
            error_count++;
        end

        if (error_count == 0)
            $display("[PASS] golay_decoder: %0d vectores verificados", checked_count);
        else
            $error("[FAIL] golay_decoder: %0d errores", error_count);

        $display("");
        $display("========================================");
        $display("");
        $finish();
    end

endmodule
