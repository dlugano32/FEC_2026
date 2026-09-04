`timescale 1ps/1ps

module golay_syndrome (
    input  wire [23 : 0] i_rx,
    output wire [11 : 0] o_syn
);

    wire [11 : 0] rx_b;

    golay_mult_b 
    u_golay_mult_b (
        .i_vec(i_rx[23 -: 12]),
        .o_vec(rx_b)
    );

    assign o_syn = rx_b ^ i_rx[11 : 0];

endmodule