`timescale 1ps/1ps

module tb_golay_row_search();

    localparam int VECTOR_COUNT = 4096;
    localparam string VECTOR_FILE = "/home/dlugano/Fulgor/FEC_2026/TP2/vectors/golay_row_search.hex";
    parameter time CLK_PERIOD = 5ns; //! 200 MHz

    logic          i_clk;
    logic [11 : 0] i_vec;
    logic          o_found;
    logic [3  : 0] o_idx;
    logic [11 : 0] o_res;

    // Cada palabra contiene {o_found, o_idx, o_res}.
    logic [16 : 0] reference [0 : VECTOR_COUNT-1];
    logic          expected_found;
    logic [3  : 0] expected_idx;
    logic [11 : 0] expected_res;

    int error_count;

    initial i_clk = 0;
    always #(CLK_PERIOD/2) i_clk = ~i_clk;

    golay_row_search
    u_golay_row_search (
        .i_vec(i_vec),
        .o_found(o_found),
        .o_idx(o_idx),
        .o_res(o_res)
    );

    initial begin
        $display("");
        $display("========================================");
        $display("Testbench de golay_row_search");
        $display("========================================");
        $display("");

        error_count = 0;
        i_vec = '0;

        $readmemh(VECTOR_FILE, reference);

        for (int i = 0; i < VECTOR_COUNT; i++) begin
            i_vec = i[11:0];
            {expected_found, expected_idx, expected_res} = reference[i];

            @(posedge i_clk)

            if ({o_found, o_idx, o_res} !== {expected_found, expected_idx, expected_res}) begin
                $error("i_vec=%03h expected=%0b_%0h_%03h obtained=%0b_%0h_%03h",
                    i_vec,
                    expected_found,
                    expected_idx,
                    expected_res,
                    o_found,
                    o_idx,
                    o_res
                );
                error_count++;
            end
        end

        if (error_count == 0)
            $display("[PASS] golay_row_search: %0d vectores verificados", VECTOR_COUNT);
        else
            $error("[FAIL] golay_row_search: %0d errores", error_count);

        $display("");
        $display("========================================");
        $display("");
        $finish();
    end

endmodule
