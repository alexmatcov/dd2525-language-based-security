dating-server:
	$(TROUPE)/bin/troupec dating-server.trp -o ./out/dating-server.js
	node $(TROUPE)/rt/built/troupe.js -f=./out/dating-server.js --id=../ids/id-server.json --trustmap=../trustmaps/GoT.json --aliases=aliases.json

dating-alice:
	$(TROUPE)/bin/troupec dating-alice.trp -o ./out/dating-alice.js
	node $(TROUPE)/rt/built/troupe.js -f=./out/dating-alice.js --id=../ids/id-alice.json --trustmap=../trustmaps/alice.json --aliases=aliases.json

