`timescale 1ps/1ps

module golay_decoder (
    input  wire          i_clk,
    input  wire          i_rst,
    input  wire [23 : 0] i_rx,
    output reg  [23 : 0] o_cw,
    output reg  [11 : 0] o_msg,
    output reg  [23 : 0] o_err,
    output reg           o_corrected,
    output reg           o_uncorrectable
);

    logic [23 : 0] rx_r;
    logic [23 : 0] rx_2_r;
    

    logic [11 : 0] syn;
    logic [3  : 0] w_syn;
    logic [3  : 0] idx_syn;
    logic          found_syn;
    logic [11 : 0] res_syn;

    logic [11 : 0] syn_r;
    logic [11 : 0] syn_2_r;
    logic [3  : 0] w_syn_r;
    logic [3  : 0] idx_syn_r;
    logic          found_syn_r;
    logic [11 : 0] res_syn_r;


    logic [11 : 0] q;
    logic [3  : 0] w_q;
    logic [3  : 0] idx_q;
    logic          found_q;
    logic [11 : 0] res_q;

    logic [11 : 0] q_r;
    logic [3  : 0] w_q_r;
    logic [3  : 0] idx_q_r;
    logic          found_q_r;
    logic [11 : 0] res_q_r;

    
    logic          syn_zero;
    logic [23 : 0] cw;
    logic [23 : 0] err;
    logic [11 : 0] msg;
    logic          corrected;
    logic          uncorrectable;

    //! Etapa 1
    golay_syndrome 
    u_golay_syndrome (
        .i_rx(i_rx),
        .o_syn(syn)
    );

    always @(posedge i_clk) begin
        if(i_rst) begin
            syn_r <= '0;
            rx_r  <= '0;
        end else begin
            syn_r <= syn;
            rx_r  <= i_rx;
        end
    end

    //! Etapa 2

    // Syndrome
    popcount12 
    u_popcount12_syn (
        .i_vec(syn_r),
        .o_weight(w_syn)
    );

    golay_row_search
    u_golay_row_search_syn (
        .i_vec(syn_r),
        .o_found(found_syn),
        .o_idx(idx_syn),
        .o_res(res_syn)
    );

    // q
    golay_mult_b 
    u_golay_mult_b_q (
        .i_vec(syn_r),
        .o_vec(q)
    );

    popcount12 
    u_popcount12_q (
        .i_vec(q),
        .o_weight(w_q)
    );

    golay_row_search
    u_golay_row_search_q (
        .i_vec(q),
        .o_found(found_q),
        .o_idx(idx_q),
        .o_res(res_q)
    );

    always @(posedge i_clk) begin
        if(i_rst) begin
            rx_2_r      <= '0;

            syn_2_r     <= '0;
            w_syn_r     <= '0;
            idx_syn_r   <= '0;
            found_syn_r <= '0;
            res_syn_r   <= '0;

            q_r         <= '0;
            w_q_r       <= '0;
            idx_q_r     <= '0;
            found_q_r   <= '0;
            res_q_r     <= '0;
        end else begin
            rx_2_r      <= rx_r;

            syn_2_r     <= syn_r;
            w_syn_r     <= w_syn;
            idx_syn_r   <= idx_syn;
            found_syn_r <= found_syn;
            res_syn_r   <= res_syn;

            q_r         <= q;
            w_q_r       <= w_q;
            idx_q_r     <= idx_q;
            found_q_r   <= found_q;
            res_q_r     <= res_q;
        end
    end

    //! Etapa 3
    golay_err_gen 
    u_golay_err_gen (
        .i_syn(syn_2_r),
        .i_res_syn(res_syn_r),
        .i_w_syn(w_syn_r),
        .i_idx_syn(idx_syn_r),
        .i_found_syn(found_syn_r),

        .i_q(q_r),
        .i_res_q(res_q_r),
        .i_w_q(w_q_r),
        .i_idx_q(idx_q_r),
        .i_found_q(found_q_r),

        .o_err(err),
        .o_uncorrectable(uncorrectable)
    );

    golay_correct
    u_golay_correct (
        .i_rx(rx_2_r),
        .i_err(err),
        .o_cw(cw),
        .o_msg(msg),
        .o_corrected(corrected)
    );

    assign syn_zero = ~(|syn_2_r);

    always_ff @( posedge i_clk ) begin
        if(i_rst) begin
            o_cw            <= '0;
            o_msg           <= '0;
            o_err           <= '0;
            o_corrected     <= '0;
            o_uncorrectable <= '0;
        end else 
            if(syn_zero) begin
                o_cw            <= rx_2_r;
                o_msg           <= rx_2_r[23 -: 12];
                o_err           <= '0;
                o_corrected     <= '0;
                o_uncorrectable <= '0;
            end else begin
                o_cw            <= cw;
                o_msg           <= msg;
                o_err           <= err;
                o_corrected     <= corrected;
                o_uncorrectable <= uncorrectable;
            end
    end

endmodule