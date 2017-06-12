/*
  Copyright (c) 2016-2017 University of Helsinki

  Permission is hereby granted, free of charge, to any person
  obtaining a copy of this software and associated documentation files
  (the "Software"), to deal in the Software without restriction,
  including without limitation the rights to use, copy, modify, merge,
  publish, distribute, sublicense, and/or sell copies of the Software,
  and to permit persons to whom the Software is furnished to do so,
  subject to the following conditions:

  The above copyright notice and this permission notice shall be
  included in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
  BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
  ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
 */

package fi.hiit.dime;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import fi.hiit.dime.data.Profile;
import fi.hiit.dime.xdi.XdiService;
import xdi2.client.XDIClientRoute;
import xdi2.client.exceptions.Xdi2ClientException;
import xdi2.client.impl.XDIAbstractClient;
import xdi2.client.impl.local.XDILocalClient;
import xdi2.core.ContextNode;
import xdi2.core.Graph;
import xdi2.core.bootstrap.XDIBootstrap;
import xdi2.core.exceptions.Xdi2Exception;
import xdi2.core.features.aggregation.Aggregation;
import xdi2.core.features.linkcontracts.instance.ConnectLinkContract;
import xdi2.core.features.linkcontracts.instance.RootLinkContract;
import xdi2.core.syntax.XDIAddress;
import xdi2.core.syntax.XDIArc;
import xdi2.core.util.XDIAddressUtil;
import xdi2.core.util.iterators.EmptyIterator;
import xdi2.core.util.iterators.ReadOnlyIterator;
import xdi2.messaging.Message;
import xdi2.messaging.MessageEnvelope;
import xdi2.messaging.container.MessagingContainer;
import xdi2.messaging.operations.Operation;

/**
 * Requests API controller.
 *
 * @author Markus Sabadello, markus@danubetech.com
 */
@RestController
@RequestMapping("/api/requests")
public class RequestsController extends AuthorizedController {

	private static final Logger LOG = LoggerFactory.getLogger(RequestsController.class);

	RequestsController() {
	}

	@RequestMapping(value="/send/{target}", method = RequestMethod.POST)
	public ResponseEntity<String>
	requestsSend(Authentication auth, @PathVariable String target)
			throws NotFoundException, BadRequestException
	{
		Profile profile = XdiService.get().profileDAO.profilesForUser(getUser(auth).getId()).get(0);
		XDIAddress didXDIAddress = XdiService.getProfileDidXDIAddress(profile);

		XDIAddress targetXDIAddress = XDIAddress.create(target);

		// find XDI route

		XDIClientRoute<?> route;

		try {

			route = XdiService.get().getXDIAgent().route(targetXDIAddress);
		} catch (Xdi2Exception ex) {

			throw new RuntimeException(ex.getMessage(), ex);
		}

		// build XDI message

		Message message = route.createMessage(didXDIAddress, -1);
		message.setFromXDIAddress(didXDIAddress);
		message.setToXDIAddress(targetXDIAddress);
		message.setLinkContractClass(ConnectLinkContract.class);
		Operation operation = message.createConnectOperation(XDIBootstrap.GET_LINK_CONTRACT_TEMPLATE_ADDRESS);
		operation.setVariableValue(XDIArc.create("{$get}"), XDIAddressUtil.concatXDIAddresses(targetXDIAddress, XDIAddress.create("#dime")));

		// send to XDI target

		XDIAbstractClient<?> client = (XDIAbstractClient<?>) route.constructXDIClient();

		try {

/*			RSASignatureCreator signatureCreator = new RSAGraphPrivateKeySignatureCreator(XdiService.get().myGraph(getUser(auth)));
			SigningManipulator manipulator = new SigningManipulator();
			manipulator.setSignatureCreator(signatureCreator);
			client.getManipulators().addManipulator(manipulator);*/

			client.send(message.getMessageEnvelope());
		} catch (Xdi2ClientException ex) {

			throw new RuntimeException(ex.getMessage(), ex);
		}

		// done

		return new ResponseEntity<String>(HttpStatus.NO_CONTENT);
	}

	@RequestMapping(value="/view", method = RequestMethod.GET)
	public ResponseEntity<List<XdiRequest>>
	requestsView(Authentication auth)
			throws NotFoundException, BadRequestException
	{
		List<XdiRequest> result = new ArrayList<XdiRequest> ();

		for (Profile profile : XdiService.get().profileDAO.profilesForUser(getUser(auth).getId())) {

			// look in XDI graph
	
			Graph graph = XdiService.get().myGraph(profile);
			if (graph == null) continue;

			ContextNode requestsContextNode = graph.getDeepContextNode(XDIAddress.create("[$msg]"));
			ReadOnlyIterator<ContextNode> requestContextNodes = requestsContextNode == null ? new EmptyIterator<ContextNode> () : Aggregation.getAggregationContextNodes(requestsContextNode);

			// result

			for (ContextNode requestContextNode : requestContextNodes) {

				Message requestMessage = Message.fromContextNode(requestContextNode);
				String address = requestMessage.getContextNode().getXDIAddress().toString();
				String from = requestMessage.getFromXDIAddress().toString();
				String operation = "" + requestMessage.getOperations().next().getOperationXDIAddress();
				String operationTarget = "" + requestMessage.getOperations().next().getTargetXDIAddress();
				Map<String, Object> operationVariables = new HashMap<String, Object> ();

				for (Entry<XDIArc, Object> variableValue : requestMessage.getOperations().next().getVariableValues().entrySet()) {

					String key = variableValue.getKey().toString();
					Object value;
					
					if (variableValue.getValue() instanceof List) {
						
						List<String> valueList = new ArrayList<String> ();
						for (Object item : ((List<?>) variableValue.getValue())) valueList.add("" + item);
						value = valueList;
					} else {
						
						value = "" + variableValue.getValue();
					}
					
					operationVariables.put(key, value);
				}

				result.add(new XdiRequest(
						address, 
						from,
						operation,
						operationTarget,
						operationVariables));
			}
		}

		// done

		return new ResponseEntity<List<XdiRequest>>(result, HttpStatus.OK);
	}

	@RequestMapping(value="/approve/{address}", method = RequestMethod.POST)
	public ResponseEntity<String>
	requestsApprove(Authentication auth, @PathVariable String address)
			throws NotFoundException, BadRequestException
	{
		XDIAddress XDIaddress = XDIAddress.create(address);
		boolean found = false;

		for (Profile profile : XdiService.get().profileDAO.profilesForUser(getUser(auth).getId())) {

			XDIAddress didXDIAddress = XdiService.getProfileDidXDIAddress(profile);

			// look in XDI graph

			Graph graph = XdiService.get().myGraph(profile);
			ContextNode requestContextNode = graph.getDeepContextNode(XDIaddress);
			Message requestMessage = requestContextNode == null ? null : Message.fromContextNode(requestContextNode);

			if (requestMessage == null) continue; else found = true;

			// XDI request to local messaging container

			try {

				MessagingContainer messagingContainer = XdiService.get().myMessagingContainer(profile);
				MessageEnvelope messageEnvelope = new MessageEnvelope();
				Message message = messageEnvelope.createMessage(didXDIAddress, -1);
				message.setFromXDIAddress(didXDIAddress);
				message.setToXDIAddress(didXDIAddress);
				message.setLinkContractClass(RootLinkContract.class);
				message.createSendOperation(requestMessage);
				message.createDelOperation(XDIaddress);

				XDILocalClient client = new XDILocalClient(messagingContainer);
				client.send(messageEnvelope);
			} catch (Xdi2ClientException ex) {

				LOG.error("Cannot execute local XDI message: " + ex.getMessage(), ex);
				return new ResponseEntity<String>(HttpStatus.INTERNAL_SERVER_ERROR);
			}
		}

		// done

		return found ? new ResponseEntity<String>(HttpStatus.NO_CONTENT) : new ResponseEntity<String>(HttpStatus.NOT_FOUND);
	}

	@RequestMapping(value="/delete", method = RequestMethod.POST)
	public ResponseEntity<String>
	requestsDelete(Authentication auth, @RequestParam String address)
			throws NotFoundException, BadRequestException
	{
		XDIAddress XDIaddress = XDIAddress.create(address);

		for (Profile profile : XdiService.get().profileDAO.profilesForUser(getUser(auth).getId())) {

			XDIAddress didXDIAddress = XdiService.getProfileDidXDIAddress(profile);

			// XDI request to local messaging container

			try {

				MessagingContainer messagingContainer = XdiService.get().myLocalMessagingContainer(profile);
				MessageEnvelope messageEnvelope = new MessageEnvelope();
				Message message = messageEnvelope.createMessage(didXDIAddress, -1);
				message.setFromXDIAddress(didXDIAddress);
				message.setToXDIAddress(didXDIAddress);
				message.setLinkContractClass(RootLinkContract.class);
				message.createDelOperation(XDIaddress);

				XDILocalClient client = new XDILocalClient(messagingContainer);
				client.send(messageEnvelope);
			} catch (Xdi2ClientException ex) {

				LOG.error("Cannot execute local XDI message: " + ex.getMessage(), ex);
				return new ResponseEntity<String>(HttpStatus.INTERNAL_SERVER_ERROR);
			}
		}

		// done

		return new ResponseEntity<String>(HttpStatus.NO_CONTENT);
	}

	private static class XdiRequest {
		public String address;
		public String from;
		public String operation;
		public String operationTarget;
		public Map<String, Object> operationVariables;
		public XdiRequest(String address, String from, String operation, String operationTarget, Map<String, Object> operationVariables) { this.address = address; this.from = from; this.operation = operation; this.operationTarget = operationTarget; this.operationVariables = operationVariables; } 
	}
}
