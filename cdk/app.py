#!/usr/bin/env python3
import aws_cdk as cdk
from dotenv import load_dotenv

from cdk.stack import RSSMusicPlayerStack
from cdk.stages import CURRENT_STAGE, Stage


load_dotenv()

if CURRENT_STAGE == Stage.PRODUCTION:
    print("Synthesizing for production environment.")
else:
    print("Synthesizing for development environment.")

app = cdk.App()

RSSMusicPlayerStack(app, "RSSMusicPlayerStack")

app.synth()

print(
    "\033[91m"
    "REMINDER: If you are manually deploying this template, run the script to rotate "
    "the database secret after deployment completes! It will be used in the "
    "CloudFormation template and migration function environment variables."
    "\033[0m"
)
