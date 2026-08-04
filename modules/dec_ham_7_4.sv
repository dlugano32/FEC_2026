module dec_ham_7_4 (
    input  logic [6 : 0] i_cw,
    output logic [3 : 0] o_m,
    output logic         o_corr
);


    // Convención:
    // i_cw = {m0, m1, m2, m3, p0, p1, p2}

    //     | 1 0 1 1 | 1 0 0 |
    // H = | 1 1 1 0 | 0 1 0 |
    //     | 0 1 1 1 | 0 0 1 |
    //          P^t      I

    logic [2 : 0] syndrome_w;
    logic [6 : 0] corr_cw_w;

    always_comb begin
        // syndrome_w = {s0, s1, s2}

        syndrome_w[2] = i_cw[6] ^ i_cw[4] ^ i_cw[3] ^ i_cw[2];  //s0
        syndrome_w[1] = i_cw[6] ^ i_cw[5] ^ i_cw[4] ^ i_cw[1];  //s1
        syndrome_w[0] = i_cw[5] ^ i_cw[4] ^ i_cw[3] ^ i_cw[0];  //s2
    end

    always_comb begin
        case (syndrome_w)
            // Sin error
            3'b000: corr_cw_w = i_cw;

            // Error en p2: i_cw[0]
            3'b001: corr_cw_w = i_cw ^ 7'b0000001;

            // Error en p1: i_cw[1]
            3'b010: corr_cw_w = i_cw ^ 7'b0000010;

            // Error en m1: i_cw[5]
            3'b011: corr_cw_w = i_cw ^ 7'b0100000;

            // Error en p0: i_cw[2]
            3'b100: corr_cw_w = i_cw ^ 7'b0000100;

            // Error en m3: i_cw[3]
            3'b101: corr_cw_w = i_cw ^ 7'b0001000;

            // Error en m0: i_cw[6]
            3'b110: corr_cw_w = i_cw ^ 7'b1000000;

            // Error en m2: i_cw[4]
            3'b111: corr_cw_w = i_cw ^ 7'b0010000;

            default: corr_cw_w = i_cw;
        endcase
    end

    // Vale 1 cuando se encontró y corrigió un error
    assign o_corr = syndrome_w[0]|syndrome_w[1]|syndrome_w[2];

    // Extraer los bits sistemáticos ya corregidos
    assign o_m = corr_cw_w[6 : 3];

endmodule