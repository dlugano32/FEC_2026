module gen_ham_7_4 (
    output logic [6 : 0] o_cw,
    input  logic [3 : 0] i_m,
    input  logic         i_clk,
    input  logic         i_rst_n,
    input  logic         i_en
);

    // Convención:
    // i_m  = {m0, m1, m2, m3}
    // o_cw = {m0, m1, m2, m3, p0, p1, p2}

    // Matriz generadora:
    // 
    //     | 1 0 0 0 | 1 1 0 |
    //     | 0 1 0 0 | 0 1 1 |
    // G = | 0 0 1 0 | 1 1 1 |
    //     | 0 0 0 1 | 1 0 1 |
    //          I        P
    
    logic [6 : 0] cw_r;
    logic [6 : 0] cw_w;

    always_ff @(posedge i_clk) begin
        if (!i_rst_n) begin
            cw_r <= '0;
        end else if (i_en) begin
            cw_r <= cw_w;
        end
    end

    // Bits de información
    assign cw_w[6 : 3] = i_m;

    // Bits de paridad
    assign cw_w[2] = i_m[3] ^ i_m[1] ^ i_m[0]; // p0
    assign cw_w[1] = i_m[3] ^ i_m[2] ^ i_m[1]; // p1
    assign cw_w[0] = i_m[2] ^ i_m[1] ^ i_m[0]; // p2

    // Salida registrada
    assign o_cw = cw_r;

endmodule