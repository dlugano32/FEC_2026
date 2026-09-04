`timescale 1ps/1ps

module golay_row_search (
    input  wire [11 : 0] i_vec,
    output wire          o_found,
    output wire [3  : 0] o_idx,
    output wire [11 : 0] o_res
);
    logic [11 : 0] v_b    [11 : 0];
    logic  [3 : 0] weight [11 : 0];

    localparam logic [11:0] B [11:0] = '{
        12'h98F,
        12'h4E7,
        12'h357,
        12'hBE2,
        12'hDD1,
        12'h7CC,
        12'h53D,
        12'h2BE,
        12'h87B,
        12'hE74,
        12'hF1A,
        12'hEA9
    };

    genvar i;

    generate
        for(i = 0; i<12; i++) begin

            assign v_b[11-i] = i_vec ^ B[11-i];

            popcount12 
            u_popcount12 (
                .i_vec(v_b[11-i]),
                .o_weight(weight[11-i])
            );
        end
    endgenerate

    assign o_found = (weight[11] <= 2) ||
                     (weight[10] <= 2) ||
                     (weight[9]  <= 2) ||
                     (weight[8]  <= 2) ||
                     (weight[7]  <= 2) ||
                     (weight[6]  <= 2) ||
                     (weight[5]  <= 2) ||
                     (weight[4]  <= 2) ||
                     (weight[3]  <= 2) ||
                     (weight[2]  <= 2) ||
                     (weight[1]  <= 2) ||
                     (weight[0]  <= 2);

    assign o_idx = (weight[11] <= 2) ? 4'd11 :
                   (weight[10] <= 2) ? 4'd10 :
                   (weight[9]  <= 2) ? 4'd9  :
                   (weight[8]  <= 2) ? 4'd8  :
                   (weight[7]  <= 2) ? 4'd7  :
                   (weight[6]  <= 2) ? 4'd6  :
                   (weight[5]  <= 2) ? 4'd5  :
                   (weight[4]  <= 2) ? 4'd4  :
                   (weight[3]  <= 2) ? 4'd3  :
                   (weight[2]  <= 2) ? 4'd2  :
                   (weight[1]  <= 2) ? 4'd1  :
                   (weight[0]  <= 2) ? 4'd0  :
                                        '0;

    assign o_res = (weight[11] <= 2) ? v_b[11]  :
                   (weight[10] <= 2) ? v_b[10]  :
                   (weight[9]  <= 2) ? v_b[9]  :
                   (weight[8]  <= 2) ? v_b[8]  :
                   (weight[7]  <= 2) ? v_b[7]  :
                   (weight[6]  <= 2) ? v_b[6]  :
                   (weight[5]  <= 2) ? v_b[5]  :
                   (weight[4]  <= 2) ? v_b[4]  :
                   (weight[3]  <= 2) ? v_b[3]  :
                   (weight[2]  <= 2) ? v_b[2]  :
                   (weight[1]  <= 2) ? v_b[1] :
                   (weight[0]  <= 2) ? v_b[0] :
                                       '0;

endmodule