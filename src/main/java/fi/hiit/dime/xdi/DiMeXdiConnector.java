package fi.hiit.dime.xdi;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import xdi2.core.ContextNode;
import xdi2.core.Graph;
import xdi2.core.syntax.XDIAddress;
import xdi2.messaging.container.MessagingContainer;
import xdi2.messaging.container.Prototype;
import xdi2.messaging.container.contributor.ContributorMount;
import xdi2.messaging.container.contributor.ContributorResult;
import xdi2.messaging.container.contributor.impl.AbstractContributor;
import xdi2.messaging.container.exceptions.Xdi2MessagingException;
import xdi2.messaging.container.execution.ExecutionContext;
import xdi2.messaging.operations.GetOperation;

@ContributorMount(contributorXDIAddresses={"{}#dime"})
public class DiMeXdiConnector extends AbstractContributor implements Prototype<DiMeXdiConnector> {

	private static final Logger log = LoggerFactory.getLogger(DiMeXdiConnector.class);

	public DiMeXdiConnector() {

		super();
	}

	/*
	 * Prototype
	 */

	@Override
	public DiMeXdiConnector instanceFor(PrototypingContext prototypingContext) throws Xdi2MessagingException {

		// done

		return this;
	}

	/*
	 * Init and shutdown
	 */

	@Override
	public void init(MessagingContainer messagingContainer) throws Exception {

		super.init(messagingContainer);
	}

	/*
	 * Contributor
	 */

	@Override
	public ContributorResult executeGetOnAddress(XDIAddress[] contributorXDIAddresses, XDIAddress contributorsXDIAddress, XDIAddress relativeTargetAddress, GetOperation operation, Graph operationResultGraph, ExecutionContext executionContext) throws Xdi2MessagingException {

		XDIAddress targetXDIAddress = contributorsXDIAddress;
		if (targetXDIAddress.equals("{}#dime")) return ContributorResult.DEFAULT;

		ContextNode targetContextNode = operationResultGraph.setDeepContextNode(targetXDIAddress);

		// add some mapped sample data to the response

		targetContextNode.setDeepContextNode(XDIAddress.create("<#first><#name>")).setLiteralString("Marjatta");
		targetContextNode.setDeepContextNode(XDIAddress.create("<#last><#name>")).setLiteralString("Raita");
		targetContextNode.setDeepContextNode(XDIAddress.create("<#email>")).setLiteralString("mr@gmail.com");
		targetContextNode.setDeepContextNode(XDIAddress.create("<#country>")).setLiteralString("Finland");

		// done

		return ContributorResult.DEFAULT;
	}
}
