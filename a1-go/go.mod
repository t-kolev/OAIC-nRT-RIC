//
//==================================================================================
//  Copyright (c) 2021 Samsung
//
//   Licensed under the Apache License, Version 2.0 (the "License");
//   you may not use this file except in compliance with the License.
//   You may obtain a copy of the License at
//
//       http://www.apache.org/licenses/LICENSE-2.0
//
//   Unless required by applicable law or agreed to in writing, software
//   distributed under the License is distributed on an "AS IS" BASIS,
//   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//   See the License for the specific language governing permissions and
//   limitations under the License.
//
//   This source code is part of the near-RT RIC (RAN Intelligent Controller)
//   platform project (RICP).
//==================================================================================
//
module gerrit.o-ran-sc.org/r/ric-plt/a1

go 1.16

replace gerrit.o-ran-sc.org/r/ric-plt/sdlgo => gerrit.o-ran-sc.org/r/ric-plt/sdlgo.git v0.7.0

replace gerrit.o-ran-sc.org/r/com/golog => gerrit.o-ran-sc.org/r/com/golog.git v0.0.2

require (
       gerrit.o-ran-sc.org/r/com/golog v0.0.2
	gerrit.o-ran-sc.org/r/ric-plt/sdlgo v0.7.0
	github.com/go-openapi/errors v0.19.9
	github.com/go-openapi/loads v0.19.7
	github.com/go-openapi/runtime v0.19.29
	github.com/go-openapi/spec v0.19.15
	github.com/go-openapi/strfmt v0.19.11
	github.com/go-openapi/swag v0.19.12
	github.com/go-openapi/validate v0.19.15
	github.com/jessevdk/go-flags v1.5.0
	github.com/stretchr/testify v1.6.1
	golang.org/x/net v0.0.0-20201110031124-69a78807bb2b
       k8s.io/utils v0.0.0-20210930125809-cb0fa318a74b // indirect
)
