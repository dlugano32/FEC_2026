`timescale 1ps/1ps

module tb_golay_mult_b();

    logic i_clk;
    logic [11 : 0] i_vec;
    logic [11 : 0] o_vec;

    logic [11 : 0] vec_w;

    int error_count;

    parameter time CLK_PERIOD = 5ns; //! 200 MHz

    initial i_clk = 0;
    always #(CLK_PERIOD/2) i_clk = ~i_clk;

    golay_mult_b 
    u_golay_mult_b_1 (
        .i_vec(i_vec),
        .o_vec(vec_w)
    );

    golay_mult_b 
    u_golay_mult_b_2 (
        .i_vec(vec_w),
        .o_vec(o_vec)
    );

 initial begin
        $display("");
        $display("========================================");
        $display("Testbench de golay_mult_b");
        $display("========================================");
        $display("");

        for (int i = 0; i < 4096; i++) begin
            i_vec = i[11:0];
            
            @(posedge i_clk);#1

            if (o_vec !== i_vec) begin
                $error("Mismatch: i_vec=%03h o_vec=%03h", i_vec, o_vec);
                error_count++;
            end
        end

        if (error_count == 0)
            $display("SUCCESS: error_count = 0");
        else
            $error("ERROR: error_count = %0d", error_count);

        $display("");
        $display("========================================");
        $display("");

        $finish();
    end

endmodule