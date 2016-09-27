fuckaba.bf: fuckaba.txt lib/*.txt resources/*.bin
	./preprocessor.py $< > $@

fuckaba: fuckaba.c

fuckaba.c: fuckaba.bf
	./translator.py $< > $@

clean:
	rm -f fuckaba.bf fuckaba fuckaba.c

resources/index.bin: resources/index-head.txt resources/index-body.htm
	echo | cat $< - | sed "s/$$/\r/g" | cat - resources/index-body.htm > $@

resources/redirect.bin: resources/redirect-head.txt
	echo | cat $< - | sed "s/$$/\r/g" > $@
