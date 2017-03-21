package fi.hiit.dime.xdi;

import java.util.Map.Entry;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import fi.hiit.dime.authentication.User;
import fi.hiit.dime.data.Profile;
import fi.hiit.dime.data.Tag;
import xdi2.core.ContextNode;
import xdi2.core.Graph;
import xdi2.core.features.nodetypes.XdiAttribute;
import xdi2.core.features.nodetypes.XdiAttributeCollection;
import xdi2.core.features.nodetypes.XdiEntity;
import xdi2.core.features.nodetypes.XdiEntitySingleton;
import xdi2.core.syntax.XDIAddress;
import xdi2.core.util.XDIAddressUtil;
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

		// map the user

		XDIAddress userIdXDIAddress = XDIAddressUtil.parentXDIAddress(targetXDIAddress, 1);
		String userId = XdiService.userIdFromXDIAddress(userIdXDIAddress);

		User user = findUserByUserId(userId);
		if (user == null) return ContributorResult.DEFAULT;

		XdiEntity userXdiEntity = XdiEntitySingleton.fromContextNode(targetContextNode);
		userXdiEntity.getXdiAttributeSingleton(XDIAddress.create("<#username>"), true).setLiteralString(user.username);
		userXdiEntity.getXdiAttributeSingleton(XDIAddress.create("<#email>"), true).setLiteralString(user.email);
		userXdiEntity.getXdiAttributeSingleton(XDIAddress.create("<#role>"), true).setLiteralString(user.role.name());

		// map all profiles

		for (Profile profile : XdiService.get().profileDAO.profilesForUser(user.getId())) {

			// map the profile

			XDIAddress profileXdiEntityXDIAddress = XDIAddressFromProfileName(profile.name);
			XdiEntity profileXdiEntity = userXdiEntity.getXdiEntity(profileXdiEntityXDIAddress, true);

			// map the tags

			if (profile.tags != null) for (Tag tag : profile.tags) {

				XdiAttributeCollection tagsXdiAttributeCollection = profileXdiEntity.getXdiAttributeCollection(XDIAddress.create("[<#tag>]"), true);
				tagsXdiAttributeCollection.setXdiInstanceOrdered().setLiteralString(tag.text);
			}

			// map the attributes

			if (profile.attributes != null) for (Entry<String, String> entry : profile.attributes.entrySet()) {

				String key = entry.getKey();
				String value = entry.getValue();

				XDIAddress attributeXdiAttributeXDIAddress = XDIAddressFromProfileAttributeKey(key);
				XdiAttribute attributeXdiAttribute = profileXdiEntity.getXdiAttributeSingleton(attributeXdiAttributeXDIAddress, true);
				attributeXdiAttribute.setLiteralString(value);
			}
		}

		// done

		return ContributorResult.DEFAULT;
	}

	/*
	 * Helper methods
	 */

	private static User findUserByUserId(String userId) {

		for (User user : XdiService.get().userDAO.findAll()) {

			if (userId.equals(user.userId)) return user;
		}

		return null;
	}

	private static XDIAddress XDIAddressFromProfileName(String name) {

		return XDIAddress.create("#" + name.replace(" ", ""));
	}

	private static XDIAddress XDIAddressFromProfileAttributeKey(String key) {

		return XDIAddress.create("<#" + key.replace(" ", "") + ">");
	}
}
