`timescale 1ps/1ps

module tb_golay_encoder();

    localparam int VECTOR_COUNT = 4096;
    localparam string VECTOR_FILE = "/home/dlugano/Fulgor/FEC_2026/TP2/vectors/golay_codewords.hex";
    parameter time CLK_PERIOD = 5ns; //! 200 MHz

    logic          i_clk;
    logic          i_rst;
    logic [11 : 0] i_msg;
    logic [23 : 0] o_cw;

    logic [23 : 0] reference [0 : VECTOR_COUNT-1];

    int error_count;

    initial i_clk = 0;
    always #(CLK_PERIOD/2) i_clk = ~i_clk;


    golay_encoder
    u_golay_encoder (
        .i_clk(i_clk),
        .i_rst(i_rst),
        .i_msg(i_msg),
        .o_cw(o_cw)
    );

    initial begin
        $display("");
        $display("========================================");
        $display("Testbench de golay_encoder");
        $display("========================================");
        $display("");

        error_count = 0;

        // Estado de reset
        i_rst = 1'b1;
        i_msg = '0;

        $readmemh(VECTOR_FILE, reference);

        repeat(2) @(negedge i_clk);

        i_rst = 1'b0;

        for (int i = 0; i < VECTOR_COUNT; i++) begin
            i_msg = i[11:0];

            @(posedge i_clk); #1;

            if (o_cw !== reference[i]) begin
                $error("i_msg=%03h expected=%06h obtained=%06h", i_msg, reference[i], o_cw);
                error_count++;
            end
        end

        if (error_count == 0)
            $display("[PASS] golay_encoder: %0d codewords verificadas", VECTOR_COUNT);
        else
            $error("[FAIL] golay_encoder: %0d errores", error_count);

        $display("");
        $display("========================================");
        $display("");
        $finish();
    end

endmodule
