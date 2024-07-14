/*
==================================================================================
  Copyright (c) 2021 Samsung

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   This source code is part of the near-RT RIC (RAN Intelligent Controller)
   platform project (RICP).
==================================================================================
*/
package main

import (
       "gerrit.o-ran-sc.org/r/ric-plt/a1/pkg/a1"
       "gerrit.o-ran-sc.org/r/ric-plt/a1/pkg/restful"
)

func main() {

	// Development configuration
	// following configuration is required if we would like to communicate with SDL
	// os.Setenv("DBAAS_SERVICE_HOST", "xxxxx")
	// os.Setenv("DBAAS_SERVICE_PORT", "xxxxx")

       // initialize logger
       a1.Init()

	// start restful service to handle a1 api's
	restful := restful.NewRestful()

       a1.Logger.Info("Starting a1 mediator.")
	restful.Run()
}
