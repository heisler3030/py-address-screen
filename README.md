# py-address-screen

A Python command-line utility for cryptocurrency address screening using the Chainalysis Address Screening API. This is a Python port of the original [node-address-screen](https://github.com/heisler3030/node-address-screen) project.

## Installation

### Prerequisites

- Python 3.8 or higher
- Chainalysis API key

### Setup

1. Clone the repository:
```bash
git clone git@github.com:heisler3030/py-address-screen.git
cd py-address-screen
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your API key:
```bash
cp .env.example .env
# Edit .env and add your Chainalysis API key
```

## Configuration

Create a `.env` file in the project root with your configuration:

```env
CHAINALYSIS_API_KEY=your_api_key_here
```

## Usage

The application requires an input CSV file containing cryptocurrency addresses:

```bash
python main.py addresses.csv
```

You can optionally specify an output file:

```bash
python main.py addresses.csv results.csv
```

If no output file is specified, the application will create one by adding `_screened` to the input filename:
- `addresses.csv` → `addresses_screened.csv`

### Configuration Options

All configuration is done through the `.env` file or environment variables:

- `CHAINALYSIS_API_KEY`: Your API key (required)

## Input CSV Format

Your input CSV file should contain at least one column with cryptocurrency addresses:

```csv
address
112YsrFpvWDVf8F55wAV75j3ncApgTkVoF
112EpYNiMjtpE12vZsiFWoxncErmLcdqmJ
0xedB60566F3fD86C2CD9DB744d59f019dAE0e45a6
0x4EC7CdF61405758f5cED5E454c0B4b0F4F043DF0
```

## Output CSV Format

```csv
address,screenStatus,risk,riskReason,category,name,atm_direct,atm_indirect,bridge_direct,bridge_indirect,child abuse material_direct,child abuse material_indirect,custom address_direct,custom address_indirect,darknet market_direct,darknet market_indirect,decentralized exchange_direct,decentralized exchange_indirect,drug vendor_direct,drug vendor_indirect,erc20 token_direct,erc20 token_indirect,escort service_direct,escort service_indirect,ethereum contract_direct,ethereum contract_indirect,exchange_direct,exchange_indirect,fraud shop_direct,fraud shop_indirect,gambling_direct,gambling_indirect,hosted wallet_direct,hosted wallet_indirect,ico_direct,ico_indirect,illicit actor-org_direct,illicit actor-org_indirect,infrastructure as a service_direct,infrastructure as a service_indirect,instant exchange_direct,instant exchange_indirect,institutional platform_direct,institutional platform_indirect,lending_direct,lending_indirect,malware_direct,malware_indirect,merchant services_direct,merchant services_indirect,mining_direct,mining_indirect,mining pool_direct,mining pool_indirect,mixing_direct,mixing_indirect,nft platform - collection_direct,nft platform - collection_indirect,no kyc exchange_direct,no kyc exchange_indirect,none_direct,none_indirect,other_direct,other_indirect,p2p exchange_direct,p2p exchange_indirect,protocol privacy_direct,protocol privacy_indirect,ransomware_direct,ransomware_indirect,sanctioned entity_direct,sanctioned entity_indirect,sanctioned jurisdiction_direct,sanctioned jurisdiction_indirect,scam_direct,scam_indirect,seized funds_direct,seized funds_indirect,smart contract_direct,smart contract_indirect,special measures_direct,special measures_indirect,stolen bitcoins_direct,stolen bitcoins_indirect,stolen ether_direct,stolen ether_indirect,stolen funds_direct,stolen funds_indirect,terrorist financing_direct,terrorist financing_indirect,token smart contract_direct,token smart contract_indirect,unnamed service_direct,unnamed service_indirect,wallet_direct,wallet_indirect
112YsrFpvWDVf8F55wAV75j3ncApgTkVoF,complete,Medium,> 7% direct exposure to Scam,unnamed service,,,23618.24,,597.94,,78.76,,,,17133.5,,,,4.72,,,,11.71,,,90433112.64719,128736014.04719,,1687.08,276972.20334,397481.49334,35778.03243,180807.00243,1339.78775,1357.19775,,25.21,,67.14,2515.3737,48179.5337,18489.33613,310539.34613,,,,65.19,1496470.56164,2469336.43164,,7817.08,22198.76183,266830.07183,,16153.01,,,469697.26606,608923.64606,,,767.18875,12429.87875,451.77177,730050.47177,,,,3138.06,,,,612.58,30203784.53158,50402397.28158,,,,,,,,,,,,194.04,,57.24,,,194914364.69487,213088348.26487,,
112EpYNiMjtpE12vZsiFWoxncErmLcdqmJ,complete,Severe,Categorized as Special Measures,special measures,FinCEN 9714a Btc2pm.me aka PM2BTC 2024-09-26,5221204.27947,26294427.20947,,766499.38,825.29233,1264.11233,,,549201.64096,7383378.58096,383.09787,15875.15787,208.52426,30373.33426,,,,451.74,,,65424538.00648,236541177.40648,126456122.82816,135552333.64816,69350.63262,2417988.93262,377802.95509,7378967.20509,,9415.42,34683430.09506,36096303.31506,50521.63106,257371.98106,37992.43239,1977822.63239,117602.94898,5163195.04898,,71.99,2496.62891,84242.96891,1050364.06811,8048891.73811,,142869.37,25668.84814,1227426.75814,378636.91481,16168361.15481,,,177074665.88336,292610170.74336,,,19557.74362,339795.62362,39178588.85874,98293187.18874,,,5311802.9049,9566950.9449,,25925.63,39690.40221,162474.48221,63247.11773,1307093.24773,20.00626,9833.35626,,5139.7,,,,,,,257707.0283,1496747.4683,7142.73033,227864.70033,,,200186471.61823,323435201.49823,,
0xedB60566F3fD86C2CD9DB744d59f019dAE0e45a6,complete,Severe,> 49% direct exposure to Sanctioned Entity,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,17951556.0,17951556.0,,,,,,,,,,,,,,,17774925.481,17774925.481,,,,,,,,,,,,,,,,,,,,,,,,
0x4EC7CdF61405758f5cED5E454c0B4b0F4F043DF0,complete,Low,,,,,3.55,,1362287.58,,,,,,,263716027.41167,325213582.31167,,,,,,,,,74660043.86007,132804264.86007,,,,15578.76,,754.28,,154.84,,564.57,,,,40957.35,,2786671.26,39787312.583,81380136.573,,,,1126.84,41868943.8807,73169362.0607,,4828.97,,138410.64,,57998.65,,8173.48,,,,142898.75,,2495.1,,1414.81,,,,,,6.31,,14886.26,,,6426912.63195,10036948.94195,,,,,,,,6978.54,,,20858578.58103,40592900.13103,2361089.64654,17149752.61654,,
```

## Examples

### Example: Basic screening
```bash
python main.py example-input.csv
```

### Example: Custom output file
```bash
python main.py addresses.csv my_results.csv
```

## API Rate Limits

The Chainalysis API has rate limits. The default settings (5 requests/second, 10 concurrent) should work well for most use cases. If you experience rate limiting errors, adjust these values in your `.env` file:
