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
// This file is safe to edit. Once it exists it will not be overwritten

package restapi

import (
	"crypto/tls"
	"net/http"

	"github.com/go-openapi/errors"
	"github.com/go-openapi/runtime"
	"github.com/go-openapi/runtime/middleware"

       "gerrit.o-ran-sc.org/r/ric-plt/a1/pkg/restapi/operations"
       "gerrit.o-ran-sc.org/r/ric-plt/a1/pkg/restapi/operations/a1_e_i_data_delivery"
       "gerrit.o-ran-sc.org/r/ric-plt/a1/pkg/restapi/operations/a1_mediator"
)

//go:generate swagger generate server --target ../../pkg --name A1 --spec ../../api/swagger.yaml --exclude-main

func configureFlags(api *operations.A1API) {
	// api.CommandLineOptionsGroups = []swag.CommandLineOptionsGroup{ ... }
}

func configureAPI(api *operations.A1API) http.Handler {
	// configure the api here
	api.ServeError = errors.ServeError

	// Set your custom logger if needed. Default one is log.Printf
	// Expected interface func(string, ...interface{})
	//
	// Example:
	// api.Logger = log.Printf

	api.JSONConsumer = runtime.JSONConsumer()

	api.JSONProducer = runtime.JSONProducer()

	if api.A1MediatorA1ControllerCreateOrReplacePolicyInstanceHandler == nil {
		api.A1MediatorA1ControllerCreateOrReplacePolicyInstanceHandler = a1_mediator.A1ControllerCreateOrReplacePolicyInstanceHandlerFunc(func(params a1_mediator.A1ControllerCreateOrReplacePolicyInstanceParams) middleware.Responder {
			return middleware.NotImplemented("operation a1_mediator.A1ControllerCreateOrReplacePolicyInstance has not yet been implemented")
		})
	}
	if api.A1MediatorA1ControllerCreatePolicyTypeHandler == nil {
		api.A1MediatorA1ControllerCreatePolicyTypeHandler = a1_mediator.A1ControllerCreatePolicyTypeHandlerFunc(func(params a1_mediator.A1ControllerCreatePolicyTypeParams) middleware.Responder {
			return middleware.NotImplemented("operation a1_mediator.A1ControllerCreatePolicyType has not yet been implemented")
		})
	}
	if api.A1eiDataDeliveryA1ControllerDataDeliveryHandler == nil {
		api.A1eiDataDeliveryA1ControllerDataDeliveryHandler = a1_e_i_data_delivery.A1ControllerDataDeliveryHandlerFunc(func(params a1_e_i_data_delivery.A1ControllerDataDeliveryParams) middleware.Responder {
			return middleware.NotImplemented("operation a1_e_i_data_delivery.A1ControllerDataDelivery has not yet been implemented")
		})
	}
	if api.A1MediatorA1ControllerDeletePolicyInstanceHandler == nil {
		api.A1MediatorA1ControllerDeletePolicyInstanceHandler = a1_mediator.A1ControllerDeletePolicyInstanceHandlerFunc(func(params a1_mediator.A1ControllerDeletePolicyInstanceParams) middleware.Responder {
			return middleware.NotImplemented("operation a1_mediator.A1ControllerDeletePolicyInstance has not yet been implemented")
		})
	}
	if api.A1MediatorA1ControllerDeletePolicyTypeHandler == nil {
		api.A1MediatorA1ControllerDeletePolicyTypeHandler = a1_mediator.A1ControllerDeletePolicyTypeHandlerFunc(func(params a1_mediator.A1ControllerDeletePolicyTypeParams) middleware.Responder {
			return middleware.NotImplemented("operation a1_mediator.A1ControllerDeletePolicyType has not yet been implemented")
		})
	}
	if api.A1MediatorA1ControllerGetAllInstancesForTypeHandler == nil {
		api.A1MediatorA1ControllerGetAllInstancesForTypeHandler = a1_mediator.A1ControllerGetAllInstancesForTypeHandlerFunc(func(params a1_mediator.A1ControllerGetAllInstancesForTypeParams) middleware.Responder {
			return middleware.NotImplemented("operation a1_mediator.A1ControllerGetAllInstancesForType has not yet been implemented")
		})
	}
	if api.A1MediatorA1ControllerGetAllPolicyTypesHandler == nil {
		api.A1MediatorA1ControllerGetAllPolicyTypesHandler = a1_mediator.A1ControllerGetAllPolicyTypesHandlerFunc(func(params a1_mediator.A1ControllerGetAllPolicyTypesParams) middleware.Responder {
			return middleware.NotImplemented("operation a1_mediator.A1ControllerGetAllPolicyTypes has not yet been implemented")
		})
	}
	if api.A1MediatorA1ControllerGetHealthcheckHandler == nil {
		api.A1MediatorA1ControllerGetHealthcheckHandler = a1_mediator.A1ControllerGetHealthcheckHandlerFunc(func(params a1_mediator.A1ControllerGetHealthcheckParams) middleware.Responder {
			return middleware.NotImplemented("operation a1_mediator.A1ControllerGetHealthcheck has not yet been implemented")
		})
	}
	if api.A1MediatorA1ControllerGetPolicyInstanceHandler == nil {
		api.A1MediatorA1ControllerGetPolicyInstanceHandler = a1_mediator.A1ControllerGetPolicyInstanceHandlerFunc(func(params a1_mediator.A1ControllerGetPolicyInstanceParams) middleware.Responder {
			return middleware.NotImplemented("operation a1_mediator.A1ControllerGetPolicyInstance has not yet been implemented")
		})
	}
	if api.A1MediatorA1ControllerGetPolicyInstanceStatusHandler == nil {
		api.A1MediatorA1ControllerGetPolicyInstanceStatusHandler = a1_mediator.A1ControllerGetPolicyInstanceStatusHandlerFunc(func(params a1_mediator.A1ControllerGetPolicyInstanceStatusParams) middleware.Responder {
			return middleware.NotImplemented("operation a1_mediator.A1ControllerGetPolicyInstanceStatus has not yet been implemented")
		})
	}
	if api.A1MediatorA1ControllerGetPolicyTypeHandler == nil {
		api.A1MediatorA1ControllerGetPolicyTypeHandler = a1_mediator.A1ControllerGetPolicyTypeHandlerFunc(func(params a1_mediator.A1ControllerGetPolicyTypeParams) middleware.Responder {
			return middleware.NotImplemented("operation a1_mediator.A1ControllerGetPolicyType has not yet been implemented")
		})
	}

	api.PreServerShutdown = func() {}

	api.ServerShutdown = func() {}

	return setupGlobalMiddleware(api.Serve(setupMiddlewares))
}

// The TLS configuration before HTTPS server starts.
func configureTLS(tlsConfig *tls.Config) {
	// Make all necessary changes to the TLS configuration here.
}

// As soon as server is initialized but not run yet, this function will be called.
// If you need to modify a config, store server instance to stop it individually later, this is the place.
// This function can be called multiple times, depending on the number of serving schemes.
// scheme value will be set accordingly: "http", "https" or "unix"
func configureServer(s *http.Server, scheme, addr string) {
}

// The middleware configuration is for the handler executors. These do not apply to the swagger.json document.
// The middleware executes after routing but before authentication, binding and validation
func setupMiddlewares(handler http.Handler) http.Handler {
	return handler
}

// The middleware configuration happens before anything, this middleware also applies to serving the swagger.json document.
// So this is a good place to plug in a panic handling middleware, logging and metrics
func setupGlobalMiddleware(handler http.Handler) http.Handler {
	return handler
}
