`timescale 1ps/1ps

module tb_golay_decoder();

    logic          i_clk;
    logic          i_rst;
    logic [23 : 0] i_rx;
    logic [23 : 0] o_cw;
    logic [11 : 0] o_msg;
    logic [23 : 0] o_err;
    logic          o_corrected;
    logic          o_uncorrectable;

    parameter time CLK_PERIOD = 5ns; //! 200 MHz

    initial i_clk = 0;
    always #(CLK_PERIOD/2) i_clk = ~i_clk;

    golay_decoder 
    u_golay_decoder (
        .i_clk(i_clk),
        .i_rst(i_rst),
        .i_rx(i_rx),
        .o_cw(o_cw),
        .o_msg(o_msg),
        .o_err(o_err),
        .o_corrected(o_corrected),
        .o_uncorrectable(o_uncorrectable)
    );

    initial begin
        $display("");
        $display("========================================");
        $display("Decodificador Golay (24,12)");
        $display("========================================");

        // Estado de reset
        i_rst = 1'b1;
        i_rx = '0;

        @(negedge i_clk);
        i_rst = 1'b0;
        @(negedge i_clk);

        //! Caso 0: Mensaje sin error
        i_rx = 24'hA5C9A5;

        repeat(3) @(negedge i_clk);
        
        $display(""); 
        $display("Caso 0 : Sin errores (i_rx = %0h", i_rx);
        $display("[Caso 0] o_cw = %0h", o_cw);
        $display("[Caso 0] o_msg = %0h", o_msg);
        $display("[Caso 0] o_err = %0h", o_err);
        $display("[Caso 0] o_corrected = %0b", o_corrected);
        $display("[Caso 0] o_uncorrectable = %0b", o_uncorrectable);
        
        if( (o_cw == 24'hA5C9A5)&& (o_err == '0) && (o_corrected == 0) && (o_uncorrectable == 0) )
            $display("[Caso 0] SUCCESSFUL");
        else
            $error("[Caso 0] ERROR");
        
        //! Caso 1: 3 errores en la redundancia
        i_rx = 24'hA5CBE7;

        repeat(3) @(negedge i_clk);
        
        $display("");   
        $display("Caso 1 : 3 errores en la redundancia (i_rx = %0h", i_rx);
        $display("[Caso 1] o_cw = %0h", o_cw);
        $display("[Caso 1] o_msg = %0h", o_msg);
        $display("[Caso 1] o_err = %0h", o_err);
        $display("[Caso 1] o_corrected = %0b", o_corrected);
        $display("[Caso 1] o_uncorrectable = %0b", o_uncorrectable);
        
        if( (o_cw == 24'hA5C9A5) && (24'h242) &&(o_corrected == 1) && (o_uncorrectable == 0) )
            $display("[Caso 1] SUCCESSFUL");
        else
            $error("[Caso 1] ERROR");

        //! Caso 2: 1 error en el mensaje y 2 en redundancia
        i_rx = 24'hA5D9A6;

        repeat(3) @(negedge i_clk);
        
        $display("");   
        $display("Caso 2 : 1 error en el mensaje y 2 en redundancia (i_rx = %0h", i_rx);
        $display("[Caso 2] o_cw = %0h", o_cw);
        $display("[Caso 2] o_msg = %0h", o_msg);
        $display("[Caso 2] o_err = %0h", o_err);
        $display("[Caso 2] o_corrected = %0b", o_corrected);
        $display("[Caso 2] o_uncorrectable = %0b", o_uncorrectable);
        
        if( (o_cw == 24'hA5C9A5) && (o_err == 24'h1003) &&(o_corrected == 1) && (o_uncorrectable == 0) )
            $display("[Caso 2] SUCCESSUL");
        else
            $error("[Caso 2] Error en la decodificación");

        //! Caso 3: 3 errores en el mensaje
        i_rx = 24'hFDC9A5;

        repeat(3) @(negedge i_clk);
        
        $display("");       
        $display("Caso 3 : 3 errores en el mensaje (i_rx = %0h", i_rx);
        $display("[Caso 3] o_cw = %0h", o_cw);
        $display("[Caso 3] o_msg = %0h", o_msg);
        $display("[Caso 3] o_err = %0h", o_err);
        $display("[Caso 3] o_corrected = %0b", o_corrected);
        $display("[Caso 3] o_uncorrectable = %0b", o_uncorrectable);
        
        if( (o_cw == 24'hA5C9A5) && (o_err == 24'h580000) && (o_corrected == 1) && (o_uncorrectable == 0) )
            $display("[Caso 3] SUCCESSUL");
        else
            $error("[Caso 3] ERROR");

        //! Caso 4: 2 errores en el mensaje y 1 en redundancia
        i_rx = 24'hA5F9A4;

        repeat(3) @(negedge i_clk);
        
        $display("");        
        $display("Caso 4 : 2 errores en el mensaje y 1 en redundancia (i_rx = %0h", i_rx);
        $display("[Caso 4] o_cw = %0h", o_cw);
        $display("[Caso 4] o_msg = %0h", o_msg);
        $display("[Caso 4] o_err = %0h", o_err);
        $display("[Caso 4] o_corrected = %0b", o_corrected);
        $display("[Caso 4] o_uncorrectable = %0b", o_uncorrectable);
        
        if( (o_cw == 24'hA5C9A5) && (o_err == 24'h3001) && (o_corrected == 1) && (o_uncorrectable == 0) )
            $display("[Caso 4] SUCCESSUL");
        else
            $error("[Caso 4] ERROR");

        //! Caso 5: + 3 errores
        i_rx = 24'hA5C9AA;

        repeat(3) @(negedge i_clk);

        $display("");
        $display("Caso 5 : + 3 errores (i_rx = %0h", i_rx);
        $display("[Caso 5] o_cw = %0h", o_cw);
        $display("[Caso 5] o_msg = %0h", o_msg);
        $display("[Caso 5] o_err = %0h", o_err);
        $display("[Caso 5] o_corrected = %0b", o_corrected);
        $display("[Caso 5] o_uncorrectable = %0b", o_uncorrectable);
        
        if( (o_corrected == 0) && (o_uncorrectable == 1) )
            $display("[Caso 5] SUCCESSFUL");
        else
            $error("[Caso 5] ERROR");

        $display("");
        $display("========================================");
        $display("");
        $finish();
    end
endmodule
