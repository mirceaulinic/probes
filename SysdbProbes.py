# Copyright (c) 2016 Cloudflare, Inc.  All rights reserved.
# Cloudflare, Inc. Confidential and Proprietary.

def Plugin( entMan ):
   entMan.registerConfigMount( "probes/config", "Probes::Config" )
