`timescale 1ps/1ps

module golay_mult_b (
    input  wire [11 : 0] i_vec,
    output wire [11 : 0] o_vec
);

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
        for (i = 0; i < 12; i++) begin : gen_mult
            assign o_vec[11-i] = ^(i_vec & B[11-i]);
        end
    endgenerate
    
endmodule