FEC surge para transmitir información de forma confiable en un canal de comunicación.

![[Pasted image 20260703111445.png]]

Encoder: Es la codificación para agrupar en bits o palabras a la información. Es donde se aplican FEC.

Modulación: Es la modulación tipo BPSK, QAM, PAM, etc. Es lo que prepara la señal para transmitirla por el canal. Es como transformar esos bits en niveles de tensión. 

Problema central de ingeniería. Diseñar codificador y decodificador para transmitir tan rápido/denso como sea posible, con reproducción confiable y a costo aceptable. En la realidad hay un canal físico, que tiene un limite de cantidad de información a transmitir, y lo mismo con el chip, tiene una frecuencia y un ancho de banda.

==La idea del codificador es agregar redundancia a la palabra a transmitir. El decodificador depura la salida del demodulador==

## Canal AWGN (Ruido Gaussiano)

![[Pasted image 20260703113744.png]]

La función de Q es que probabilidad hay de que el ruido presente en el canal nos "voltee" el bit o simbolo, es decir que ingrese un error.
El ebno (Eb/No) es la calidad del canal dado, es como la relación señal ruido. A mayor potencia del simbolo, mejora la calidad del canal, porque el ruido se mantiene y vos transmitis mas fuerte. Si bajas el ruido de canal, el ebno mejora tambien.

![[Pasted image 20260703115234.png]]Con codificación binaria y demodulador de decisión dura: el canal binario simétrico quiere decir, que si transmito un 1, la probalidad de que me cambie es igual a la que se transmito un 0 y me cambie.

## Hard decision & soft decision
![[Pasted image 20260703120928.png]]

## Codigos continuos
Es un codificador continuo que introduce redundancia de forma ininterrumpida, donde cada salida depende tambien de M bloques anteriores. Es decir el codificador tiene memoria y tiene en cuenta valores anteriores para tomar decisiones. Por lo tanto se adaptan mejor a la decisión suave. Su nombre es codificadores convolucionales.
==Es como una forma de contextualizar el mensaje.==

## Conceptos importantes

![[Pasted image 20260703125503.png]]

El concepto de distancia minima es muy importante porque permite saber de que codeword estamos mas cerca la hacer correcciones. Por ejemplo en RCH (7,4), Tenemos 2⁷ combinaciones de las cuales solo 2⁴ van a ser codewords utilizadas. Si por ejemplo la distancia minima fuera 5, al hacer 2 correcciones vamos a estar mas cerca de una palabra que de otra y podemos saber cual fue la palabra transmitida.

## FEC vs ARQ

![[Pasted image 20260703132954.png]]

## Interleaving

![[Pasted image 20260703133255.png]]

Lo que se hace es intercalar la trama de palabras antes de enviar de forma que los errores de rafaga queden dispersos por varias palabras en lugar de en una sola y no se pueda corregir. Luego en la corrección se los desentrama y se los puede corregir. Basicamente es como convertir errores consecutivos en aleatorios.

![[Pasted image 20260703133606.png]]