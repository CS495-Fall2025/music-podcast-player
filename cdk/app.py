#!/usr/bin/env python3

import aws_cdk as cdk

from cdk.stack import RSSMusicPlayerStack


app = cdk.App()

RSSMusicPlayerStack(app, "RSSMusicPlayerStack")

app.synth()
