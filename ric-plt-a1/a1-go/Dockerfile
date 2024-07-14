#   Copyright (c) 2021 Samsung.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

#-----------------------------------------------------------

FROM nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-ubuntu18-c-go:1.9.0 AS a1-build

RUN apt-get update -y && apt-get install -y jq

# Update CA certificates
RUN apt update && apt install --reinstall -y \
  ca-certificates \
  && \
  update-ca-certificates

ENV PATH="/usr/local/go/bin:${PATH}"

ENV GOPATH="/go"

RUN mkdir -p /go/bin
RUN mkdir -p /go/src/ws
WORKDIR "/go/src/ws"

# Module prepare (if go.mod/go.sum updated)
COPY go.mod /go/src/ws
COPY go.sum /go/src/ws
RUN GO111MODULE=on go mod download

# build and test
COPY . /go/src/ws

# Build the code
RUN GO111MODULE=on GO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o /go/src/ws/cache/go/cmd/a1 cmd/a1.go

# Run unit tests
RUN GO111MODULE=on GO_ENABLED=0 GOOS=linux go test -p 1 -cover ./pkg/resthooks/
RUN GO111MODULE=on GO_ENABLED=0 GOOS=linux go test -p 1 -cover ./pkg/a1/

RUN gofmt -l $(find cmd/ pkg/  -name '*.go' -not -name '*_test.go')

CMD ["/bin/bash"]


#----------------------------------------------------------
FROM ubuntu:18.04 as a1-mediator

RUN apt-get update -y \
    && apt-get install --reinstall -y sudo openssl ca-certificates ca-cacert \
    && apt-get clean && update-ca-certificates

#
# a1-mediator
#
RUN mkdir -p /opt/a1-mediator \
    && chmod -R 755 /opt/a1-mediator

COPY --from=a1-build /go/src/ws/cache/go/cmd/a1 /opt/a1-mediator/a1

WORKDIR /opt/a1-mediator

COPY a1-entrypoint.sh /opt/a1-mediator/
ENTRYPOINT ["/opt/a1-mediator/a1-entrypoint.sh"]

