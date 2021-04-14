solcvs = 0.7.6

test: FORCE
	poetry run python -m pytest tests/** --disable-warnings --show-capture=log

format: FORCE  # Format code using Black formatter
	poetry run black auditless_solcx/** tests/** --line-length 100
	poetry run isort --profile black src

lint: FORCE  # Lint all source code
	poetry run mypy auditless_solcx/**.py

install: FORCE  # Install dependencies (used for CI)
	poetry install
	poetry lock

install_solc: FORCE  # Install Solidity compiler (used for CI)
	mkdir -p ~/.solcx

	for solcv in $(solcvs); do \
		wget -O ./solc-$${solcv} https://github.com/ethereum/solidity/releases/download/v$${solcv}/solc-static-linux; \
		chmod +x ./solc-$${solcv}; \
		sudo cp ./solc-$${solcv} ~/.solcx/solc-v$${solcv}; \
	done

FORCE:
