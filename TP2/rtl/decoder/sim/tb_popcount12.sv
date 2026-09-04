`timescale 1ps/1ps

module tb_popcount12();

    logic i_clk;
    logic [11 : 0] i_vec;
    logic [3  : 0] o_weight;
    logic [3  : 0] reference;


    int error_count;

    parameter time CLK_PERIOD = 5ns; //! 200 MHz

    initial i_clk = 0;
    always #(CLK_PERIOD/2) i_clk = ~i_clk;

    popcount12 
    u_popcount12(
        .i_vec(i_vec),
        .o_weight(o_weight)
    );

 initial begin
        $display("");
        $display("========================================");
        $display("Testbench de golay_mult_b");
        $display("========================================");
        $display("");

        for (int i = 0; i < 4096; i++) begin
            i_vec = i[11:0];
            reference = i_vec[0] + i_vec[1] + i_vec[2]  + i_vec[3]
                      + i_vec[4] + i_vec[5] + i_vec[6]  + i_vec[7]
                      + i_vec[8] + i_vec[9] + i_vec[10] + i_vec[11];

            @(posedge i_clk);

            if (o_weight !== reference) begin
                $error("Mismatch: reference=%0d o_weight=%0d", reference, o_weight);
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