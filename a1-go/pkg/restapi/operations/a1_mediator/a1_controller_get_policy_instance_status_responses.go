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
// Code generated by go-swagger; DO NOT EDIT.

package a1_mediator

// This file was generated by the swagger tool.
// Editing this file might prove futile when you re-run the swagger generate command

import (
	"net/http"

	"github.com/go-openapi/runtime"
)

// A1ControllerGetPolicyInstanceStatusOKCode is the HTTP code returned for type A1ControllerGetPolicyInstanceStatusOK
const A1ControllerGetPolicyInstanceStatusOKCode int = 200

/*A1ControllerGetPolicyInstanceStatusOK successfully retrieved the status


swagger:response a1ControllerGetPolicyInstanceStatusOK
*/
type A1ControllerGetPolicyInstanceStatusOK struct {

	/*
	  In: Body
	*/
	Payload *A1ControllerGetPolicyInstanceStatusOKBody `json:"body,omitempty"`
}

// NewA1ControllerGetPolicyInstanceStatusOK creates A1ControllerGetPolicyInstanceStatusOK with default headers values
func NewA1ControllerGetPolicyInstanceStatusOK() *A1ControllerGetPolicyInstanceStatusOK {

	return &A1ControllerGetPolicyInstanceStatusOK{}
}

// WithPayload adds the payload to the a1 controller get policy instance status o k response
func (o *A1ControllerGetPolicyInstanceStatusOK) WithPayload(payload *A1ControllerGetPolicyInstanceStatusOKBody) *A1ControllerGetPolicyInstanceStatusOK {
	o.Payload = payload
	return o
}

// SetPayload sets the payload to the a1 controller get policy instance status o k response
func (o *A1ControllerGetPolicyInstanceStatusOK) SetPayload(payload *A1ControllerGetPolicyInstanceStatusOKBody) {
	o.Payload = payload
}

// WriteResponse to the client
func (o *A1ControllerGetPolicyInstanceStatusOK) WriteResponse(rw http.ResponseWriter, producer runtime.Producer) {

	rw.WriteHeader(200)
	if o.Payload != nil {
		payload := o.Payload
		if err := producer.Produce(rw, payload); err != nil {
			panic(err) // let the recovery middleware deal with this
		}
	}
}

// A1ControllerGetPolicyInstanceStatusNotFoundCode is the HTTP code returned for type A1ControllerGetPolicyInstanceStatusNotFound
const A1ControllerGetPolicyInstanceStatusNotFoundCode int = 404

/*A1ControllerGetPolicyInstanceStatusNotFound there is no policy instance with this policy_instance_id or there is no policy type with this policy_type_id


swagger:response a1ControllerGetPolicyInstanceStatusNotFound
*/
type A1ControllerGetPolicyInstanceStatusNotFound struct {
}

// NewA1ControllerGetPolicyInstanceStatusNotFound creates A1ControllerGetPolicyInstanceStatusNotFound with default headers values
func NewA1ControllerGetPolicyInstanceStatusNotFound() *A1ControllerGetPolicyInstanceStatusNotFound {

	return &A1ControllerGetPolicyInstanceStatusNotFound{}
}

// WriteResponse to the client
func (o *A1ControllerGetPolicyInstanceStatusNotFound) WriteResponse(rw http.ResponseWriter, producer runtime.Producer) {

	rw.Header().Del(runtime.HeaderContentType) //Remove Content-Type on empty responses

	rw.WriteHeader(404)
}

// A1ControllerGetPolicyInstanceStatusServiceUnavailableCode is the HTTP code returned for type A1ControllerGetPolicyInstanceStatusServiceUnavailable
const A1ControllerGetPolicyInstanceStatusServiceUnavailableCode int = 503

/*A1ControllerGetPolicyInstanceStatusServiceUnavailable Potentially transient backend database error. Client should attempt to retry later.

swagger:response a1ControllerGetPolicyInstanceStatusServiceUnavailable
*/
type A1ControllerGetPolicyInstanceStatusServiceUnavailable struct {
}

// NewA1ControllerGetPolicyInstanceStatusServiceUnavailable creates A1ControllerGetPolicyInstanceStatusServiceUnavailable with default headers values
func NewA1ControllerGetPolicyInstanceStatusServiceUnavailable() *A1ControllerGetPolicyInstanceStatusServiceUnavailable {

	return &A1ControllerGetPolicyInstanceStatusServiceUnavailable{}
}

// WriteResponse to the client
func (o *A1ControllerGetPolicyInstanceStatusServiceUnavailable) WriteResponse(rw http.ResponseWriter, producer runtime.Producer) {

	rw.Header().Del(runtime.HeaderContentType) //Remove Content-Type on empty responses

	rw.WriteHeader(503)
}
