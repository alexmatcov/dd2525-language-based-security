dating-server:
	$(TROUPE)/bin/troupec dating-server.trp -o ./out/dating-server.js
	node $(TROUPE)/rt/built/troupe.js -f=./out/dating-server.js --id=../ids/id-server.json --trustmap=../trustmaps/GoT.json --aliases=aliases.json

dating-alice:
	$(TROUPE)/bin/troupec dating-alice.trp -o ./out/dating-alice.js
	node $(TROUPE)/rt/built/troupe.js -f=./out/dating-alice.js --id=../ids/id-alice.json --trustmap=../trustmaps/alice.json --aliases=aliases.json

dating-bob:
	$(TROUPE)/bin/troupec dating-bob.trp -o ./out/dating-bob.js
	node $(TROUPE)/rt/built/troupe.js -f=./out/dating-bob.js --id=../ids/id-bob.json --trustmap=../trustmaps/bob.json --aliases=aliases.json

dating-malicious:
	$(TROUPE)/bin/troupec dating-malicious.trp -o ./out/dating-malicious.js
	node $(TROUPE)/rt/built/troupe.js -f=./out/dating-malicious.js --id=../ids/id-malicious.json --trustmap=../trustmaps/malicious.json --aliases=aliases.json
