#!/usr/bin/env python3
import aws_cdk as cdk

from cdk.stack import RSSMusicPlayerStack
from cdk.stages import CURRENT_STAGE, Stage


if CURRENT_STAGE == Stage.PRODUCTION:
    print("Synthesizing for production environment.")
else:
    print("Synthesizing for development environment.")

app = cdk.App()

RSSMusicPlayerStack(app, "RSSMusicPlayerStack")

app.synth()
