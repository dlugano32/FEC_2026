ARQ es automatic repeat queues. Basicamente se repite el mensaje cuando llegó con errores. 

En FEC se envian redundancias pero por unica vez.

## Entropia e incertidumbre

En un AWGN, tener probabilidad 0 o 1, no tenes incertidumbre, la fuente es predecible.
Sin embargo, la probabilidad p=0,5, la incertidumbre es máxima siempre.

![[Pasted image 20260707084258.png]]

La entropia es una forma de medir la incertidumbre.

## Capacidad de canal

![[Pasted image 20260707084614.png]]

## Teorema de Shannon : Muy importante
R = k/n ; cantidad de información en bits sobre bits transmitidos. 

![[Pasted image 20260707085814.png]]


![[Pasted image 20260707085947.png]]

P(r|v) : La probabilidad de ver r dado que se transmitió v.

## Limite de shannon
![[Pasted image 20260707090828.png]]

Lo que nos dice el teorema de limite de shannon es que existe un piso de Eb/No (-1.6dB) al cual se puede transmitir si tenemos una R tendiendo a cero (osea n tendiendo a infinito, maxima redundancia). Lo ideal es utilizar codificaciones que estén cerca de este limite, mientras mas cerca mas eficiente.