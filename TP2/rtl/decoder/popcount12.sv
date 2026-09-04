`timescale 1ps/1ps

module popcount12 (
    input  wire [11 : 0] i_vec,
    output wire [3  : 0] o_weight
);

assign o_weight = i_vec[0]
                + i_vec[1]
                + i_vec[2]
                + i_vec[3]
                + i_vec[4]
                + i_vec[5]
                + i_vec[6]
                + i_vec[7]
                + i_vec[8]
                + i_vec[9]
                + i_vec[10]
                + i_vec[11];

endmodule