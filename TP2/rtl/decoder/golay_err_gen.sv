`timescale 1ps/1ps

module golay_err_gen (
    input  wire [11 : 0] i_syn,       i_q,   i_res_syn, i_res_q,
    input  wire [3  : 0] i_w_syn,     i_w_q, i_idx_syn, i_idx_q,
    input  wire          i_found_syn, i_found_q,
    output wire [23 : 0] o_err,
    output wire          o_uncorrectable
);

    assign o_err =  (i_w_syn <= 3) ? {12'b0, i_syn}                  :
                    (i_found_syn)  ? {12'b1 << i_idx_syn, i_res_syn} :
                    (i_w_q <= 3)   ? {i_q, 12'b0}                    :
                    (i_found_q)    ? {i_res_q, 12'b1 << i_idx_q}     :
                                     '0;


    assign o_uncorrectable = ~( (i_w_syn <= 3) || 
                                (i_found_syn)  ||
                                (i_w_q <= 3)   ||
                                (i_found_q)
                            );


endmodule