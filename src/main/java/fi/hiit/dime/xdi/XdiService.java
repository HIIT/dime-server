package fi.hiit.dime.xdi;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.NoSuchBeanDefinitionException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Scope;
import org.springframework.context.support.GenericXmlApplicationContext;
import org.springframework.core.io.UrlResource;
import org.springframework.stereotype.Service;

import fi.hiit.dime.XdiController;
import fi.hiit.dime.authentication.User;
import fi.hiit.dime.data.Profile;
import fi.hiit.dime.database.ProfileDAO;
import fi.hiit.dime.database.UserDAO;
import xdi2.agent.XDIAgent;
import xdi2.core.Graph;
import xdi2.core.syntax.XDIAddress;
import xdi2.messaging.container.MessagingContainer;
import xdi2.messaging.container.impl.graph.GraphMessagingContainer;
import xdi2.messaging.container.interceptor.impl.HasInterceptor;
import xdi2.messaging.container.interceptor.impl.RefInterceptor;
import xdi2.messaging.container.interceptor.impl.connect.ConnectInterceptor;
import xdi2.messaging.container.interceptor.impl.send.SendInterceptor;
import xdi2.transport.impl.http.HttpTransport;
import xdi2.transport.registry.MessagingContainerMount;
import xdi2.transport.registry.impl.uri.UriMessagingContainerRegistry;

@Service
@Scope("singleton")
public class XdiService {

	private static final Logger LOG = LoggerFactory.getLogger(XdiService.class);

	private static XdiService instance = null;
	public UserDAO userDAO = null;
	public ProfileDAO profileDAO = null;

	private XDIAgent xdiAgent;
	private HttpTransport httpTransport;
	private UriMessagingContainerRegistry uriMessagingContainerRegistry;

	public static XdiService get() {

		return instance;
	}

	@Autowired
	public XdiService(UserDAO userDAO, ProfileDAO profileDAO) {

		LOG.debug("Initializing...");

		instance = this;
		this.userDAO = userDAO;
		this.profileDAO = profileDAO;

		GenericXmlApplicationContext applicationContext = new GenericXmlApplicationContext();
		applicationContext.load(new UrlResource(XdiController.class.getClassLoader().getResource("xdi-applicationContext.xml")));
		applicationContext.refresh();

		this.xdiAgent = (XDIAgent) applicationContext.getBean("XDIAgent");
		if (this.xdiAgent == null) throw new NoSuchBeanDefinitionException("Required bean 'XDIAgent' not found.");

		this.uriMessagingContainerRegistry = (UriMessagingContainerRegistry) applicationContext.getBean("UriMessagingContainerRegistry");
		if (this.uriMessagingContainerRegistry == null) throw new NoSuchBeanDefinitionException("Required bean 'UriMessagingContainerRegistry' not found.");

		this.httpTransport = (HttpTransport) applicationContext.getBean("HttpTransport");
		if (this.httpTransport == null) throw new NoSuchBeanDefinitionException("Required bean 'HttpTransport' not found.");

	}

	public XDIAgent getXDIAgent() {

		return xdiAgent;
	}

	public HttpTransport getHttpTransport() {

		return httpTransport;
	}

	public MessagingContainer myMessagingContainer(Profile profile) {

		XDIAddress didXDIAddress = getProfileDidXDIAddress(profile);
		if (didXDIAddress == null) return null;

		MessagingContainerMount messagingContainerMount = null;

		try {

			messagingContainerMount = uriMessagingContainerRegistry.lookup("/dime/" + didXDIAddress.toString());
		} catch (Exception ex) {

			LOG.warn("Cannot look up XDI messaging container: " + ex.getMessage(), ex);
		}

		MessagingContainer messagingContainer = messagingContainerMount == null ? null : messagingContainerMount.getMessagingContainer();
		LOG.info("Found messaging container for profile " + profile + " and DID " + didXDIAddress + ": " + messagingContainer);

		return messagingContainer;
	}

	public MessagingContainer myLocalMessagingContainer(Profile profile) {

		Graph graph = myGraph(profile);
		if (graph == null) return null;

		GraphMessagingContainer messagingContainer = new GraphMessagingContainer(graph);
		messagingContainer.getInterceptors().addInterceptor(new RefInterceptor());
		messagingContainer.getInterceptors().addInterceptor(new HasInterceptor());
		messagingContainer.getInterceptors().addInterceptor(new ConnectInterceptor(null, this.xdiAgent));
		messagingContainer.getInterceptors().addInterceptor(new SendInterceptor(this.xdiAgent));
		messagingContainer.getContributors().addContributor(new DiMeXdiConnector());

		return messagingContainer;
	}

	public Graph myGraph(Profile profile) {

		GraphMessagingContainer graphMessagingContainer = (GraphMessagingContainer) myMessagingContainer(profile);
		return graphMessagingContainer == null ? null : graphMessagingContainer.getGraph();
	}

	/*
	 * Helper methods
	 */

	/**
	 * Finds the DiMe profile associated with a given XDI identifier. 
	 */
	public static Profile findProfileByDidXDIAddress(XDIAddress didXDIAddress) {

		for (User user : XdiService.get().userDAO.findAll()) {

			for (Profile profile : XdiService.get().profileDAO.profilesForUser(user.getId())) {

				String profileDid = profile.attributes.get("did");
				if (didXDIAddress.toString().equals(profileDid)) {

					LOG.info("Found profile for DID " + didXDIAddress + ": " + profile);
					return profile;
				}
			}
		}

		LOG.info("Found profile for DID " + didXDIAddress + ": " + null);
		return null;
	}

	public static XDIAddress getProfileDidXDIAddress(Profile profile) {

		String didXDIAddressString = profile.attributes.get("did");
		XDIAddress didXDIAddress = didXDIAddressString == null ? null : XDIAddress.create(didXDIAddressString);
		LOG.info("Found DID for profile " + profile + ": " + didXDIAddress);

		return didXDIAddress;
	}

	public static void setProfileDidXDIAddress(Profile profile, XDIAddress didXDIAddress) {

		profile.attributes.put("did", didXDIAddress.toString());
		XdiService.get().profileDAO.save(profile);
		LOG.info("Set DID for profile " + profile + ": " + didXDIAddress);
	}

	/**
	 * Maps an XDI identifier to a DID.
	 * E.g. =!:did:sov:RFrnVYLnRPRrgKY5pY9MHK -> RFrnVYLnRPRrgKY5pY9MHK
	 */
	public static String didStringFromXDIAddress(XDIAddress XDIaddress) {

		return XDIaddress.toString().startsWith("=!:did:sov:") ? XDIaddress.toString().substring("=!:did:sov:".length()) : null;
	}

	/**
	 * Maps a DID to an XDI identifier.
	 * E.g. RFrnVYLnRPRrgKY5pY9MHK -> =!:did:sov:RFrnVYLnRPRrgKY5pY9MHK
	 */
	public static XDIAddress XDIAddressFromDidString(String did) {

		return XDIAddress.create("=!:did:sov:" + did);
	}

	/**
	 * Maps a DiMe profile name to an XDI identifier
	 */
	public static XDIAddress XDIAddressFromProfileName(String name) {

		return XDIAddress.create("#" + name.replace(" ", ""));
	}

	/**
	 * Maps a DiMe profile attribute key to an XDI identifier
	 */
	public static XDIAddress XDIAddressFromProfileAttributeKey(String key) {

		return XDIAddress.create("<#" + key.replace(" ", "") + ">");
	}
}
