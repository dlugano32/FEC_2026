`timescale 1ps/1ps

module golay_encoder (
    input  wire i_clk,
    input  wire i_rst,
    input  wire [11 : 0] i_msg,
    output reg  [23 : 0] o_cw
);
    wire [11 : 0] parity;

    golay_mult_b 
    u_golay_mult_b (
        .i_vec(i_msg),
        .o_vec(parity)
    );

    always_ff @( posedge i_clk ) begin
        if(i_rst) begin
            o_cw <= '0;
        end else begin
            o_cw <= {i_msg, parity};
        end
    end
endmodule