import argparse

dateparser_argparse = argparse.ArgumentParser(description='dateparser-download menager.', usage="dateparser-download [-h] [--fasttext] [--clear-cache]")
dateparser_argparse.add_argument('--fasttext',
                       type=str,
                       help='To download a fasttext language detection models. Supported models are "small" and "large"')
dateparser_argparse.add_argument('--clear','--clear-cache',
                       help='To clear all cached models',
                       action='store_true')

args = dateparser_argparse.parse_args()
fasttext = args.fasttext
clear_cache = args.clear

print(clear_cache)
