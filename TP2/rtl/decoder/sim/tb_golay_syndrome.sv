`timescale 1ps/1ps

module tb_golay_syndrome();

    localparam int CODEWORD_COUNT = 4096;
    localparam int SYNDROME_COUNT = 2325;
    parameter time CLK_PERIOD = 5ns; //! 200 MHz

    localparam string CODEWORDS_FILE = "/home/dlugano/Fulgor/FEC_2026/TP2/vectors/golay_codewords.hex";
    localparam string SYNDROMES_FILE = "/home/dlugano/Fulgor/FEC_2026/TP2/vectors/golay_syndromes_w0_w3.hex";

    logic          i_clk;

    logic [23 : 0] i_rx;
    logic [11 : 0] o_syn;

    logic [23 : 0] codewords [0 : CODEWORD_COUNT - 1];
    logic [35 : 0] reference [0 : SYNDROME_COUNT - 1];
    logic [23 : 0] input_error;
    logic [11 : 0] expected_syndrome;

    int error_count;

    initial i_clk = 0;
    always #(CLK_PERIOD/2) i_clk = ~i_clk;

    golay_syndrome
    u_golay_syndrome (
        .i_rx(i_rx),
        .o_syn(o_syn)
    );

    initial begin
        $display("");
        $display("========================================");
        $display("Testbench de golay_syndrome");
        $display("========================================");
        $display("");

        error_count = 0;
        i_rx = '0;

        $readmemh(CODEWORDS_FILE, codewords);
        $readmemh(SYNDROMES_FILE, reference);

        // Toda palabra codigo debe tener sindrome nulo.
        for (int i = 0; i < CODEWORD_COUNT; i++) begin
            i_rx = codewords[i];
            
            @(posedge i_clk);

            if (o_syn !== 12'h000) begin
                $error("Codeword[%0d]=%06h: expected syndrome=000 obtained=%03h", i, i_rx, o_syn);
                error_count++;
            end
        end

        // Sindrome esperado para cada error de peso 0 a 3.
        for (int i = 0; i < SYNDROME_COUNT; i++) begin
            {input_error, expected_syndrome} = reference[i];
            i_rx = input_error;
            
            @(posedge i_clk);

            if (o_syn !== expected_syndrome) begin
                $error("Error[%0d]=%06h: expected syndrome=%03h obtained=%03h", i, input_error, expected_syndrome, o_syn);
                error_count++;
            end
        end

        if (error_count == 0) begin
            $display("[PASS] golay_syndrome: %0d codewords y %0d errores verificados", CODEWORD_COUNT, SYNDROME_COUNT);
        end else begin
            $error("[FAIL] golay_syndrome: %0d errores", error_count);
        end

        $display("");
        $display("========================================");
        $display("");
        $finish();
    end

endmodule
