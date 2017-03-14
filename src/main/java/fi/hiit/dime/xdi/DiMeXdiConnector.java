package fi.hiit.dime.xdi;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import fi.hiit.dime.authentication.User;
import fi.hiit.dime.data.Profile;
import fi.hiit.dime.data.Tag;
import fi.hiit.dime.database.ProfileDAO;
import fi.hiit.dime.database.UserDAO;
import xdi2.core.ContextNode;
import xdi2.core.Graph;
import xdi2.core.features.nodetypes.XdiAttribute;
import xdi2.core.features.nodetypes.XdiAttributeCollection;
import xdi2.core.features.nodetypes.XdiEntity;
import xdi2.core.features.nodetypes.XdiEntitySingleton;
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

	private UserDAO userDAO;
	private ProfileDAO profileDAO;

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

		// get a user and profile

		User user = this.userDAO.findByUsername("peacekeeper");
		Profile profile = this.profileDAO.profilesForUser(user.getId()).get(0);

		// add some mapped sample data to the response

		XdiEntity userXdiEntity = XdiEntitySingleton.fromContextNode(targetContextNode);

		userXdiEntity.getXdiAttributeSingleton(XDIAddress.create("<#first><#name>"), true).setLiteralString("Test FIrst Name");
		userXdiEntity.getXdiAttributeSingleton(XDIAddress.create("<#last><#name>"), true).setLiteralString("Test Last Name");
		userXdiEntity.getXdiAttributeSingleton(XDIAddress.create("<#email>"), true).setLiteralString(user.email);

		XdiAttribute roleXdiAttribute = userXdiEntity.getXdiAttributeSingleton(XDIAddress.create("<#role>"), true);
		roleXdiAttribute.setLiteralString(user.role.name());

		XdiEntity profileXdiEntity = XdiEntitySingleton.fromContextNode(targetContextNode.setDeepContextNode(XDIAddress.create("#profile")));
		profileXdiEntity.getXdiAttributeSingleton(XDIAddress.create("<#name>"), true).setLiteralString(profile.name);

		for (Tag tag : profile.tags) {

			XdiAttributeCollection tagsXdiAttributeCollection = profileXdiEntity.getXdiAttributeCollection(XDIAddress.create("[<#tag>]"), true);
			tagsXdiAttributeCollection.setXdiInstanceOrdered().setLiteralString(tag.text);
		}

		// done

		return ContributorResult.DEFAULT;
	}

	/*
	 * Getters and setters
	 */

	public UserDAO getUserDAO() {

		return this.userDAO;
	}

	public void setUserDAO(UserDAO userDAO) {

		this.userDAO = userDAO;
	}

	public ProfileDAO getProfileDAO() {

		return this.profileDAO;
	}

	public void setProfileDAO(ProfileDAO profileDAO) {

		this.profileDAO = profileDAO;
	}
}
