fuckaba.bf: fuckaba.txt preprocessor.py lib/*.txt resources/*.bin
	./preprocessor.py $< > $@

fuckaba: fuckaba.c

fuckaba.c: fuckaba.bf translator.py
	./translator.py $< > $@

awoken: awoken.c

awoken.c: dump.bin translator.py
	./translator.py -s $< > $@

clean:
	rm -f fuckaba fuckaba.c awoken awoken.c

resources/index.bin: resources/index-head.txt resources/index-body.htm
	echo | cat $< - | sed "s/$$/\r/g" | cat - resources/index-body.htm > $@

resources/redirect.bin: resources/redirect-head.txt
	echo | cat $< - | sed "s/$$/\r/g" > $@
