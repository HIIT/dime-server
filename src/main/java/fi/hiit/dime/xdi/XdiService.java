package fi.hiit.dime.xdi;

import java.util.ArrayList;

import org.springframework.beans.factory.NoSuchBeanDefinitionException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Scope;
import org.springframework.context.support.GenericXmlApplicationContext;
import org.springframework.core.io.UrlResource;
import org.springframework.stereotype.Service;

import fi.hiit.dime.XdiController;
import fi.hiit.dime.authentication.User;
import fi.hiit.dime.database.ProfileDAO;
import fi.hiit.dime.database.UserDAO;
import xdi2.agent.XDIAgent;
import xdi2.client.manipulator.Manipulator;
import xdi2.core.Graph;
import xdi2.core.syntax.XDIAddress;
import xdi2.messaging.container.MessagingContainer;
import xdi2.messaging.container.impl.graph.GraphMessagingContainer;
import xdi2.messaging.container.interceptor.impl.HasInterceptor;
import xdi2.messaging.container.interceptor.impl.RefInterceptor;
import xdi2.messaging.container.interceptor.impl.connect.ConnectInterceptor;
import xdi2.messaging.container.interceptor.impl.send.SendInterceptor;
import xdi2.transport.impl.http.HttpTransport;
import xdi2.transport.registry.impl.uri.UriMessagingContainerRegistry;

@Service
@Scope("singleton")
public class XdiService {

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

	public MessagingContainer myMessagingContainer(User user) {

		return uriMessagingContainerRegistry.getMessagingContainer("/dime");
	}

	public MessagingContainer myLocalMessagingContainer(User user) {

		GraphMessagingContainer messagingContainer = new GraphMessagingContainer(myGraph(user));
		messagingContainer.getInterceptors().addInterceptor(new RefInterceptor());
		messagingContainer.getInterceptors().addInterceptor(new HasInterceptor());
		messagingContainer.getInterceptors().addInterceptor(new ConnectInterceptor(null, this.xdiAgent));
		messagingContainer.getInterceptors().addInterceptor(new SendInterceptor(this.xdiAgent));
		messagingContainer.getContributors().addContributor(new DiMeXdiConnector());

		return messagingContainer;
	}

	public Graph myGraph(User user) {

		return ((GraphMessagingContainer) myMessagingContainer(user)).getGraph();
	}

	/*
	 * Helper methods
	 */
	
	/**
	 * Maps an XDI identifier to a DiMe user ID.
	 * E.g. =!:uuid:e1ea806e-3ecd-4827-adbe-2a76ab178d54 -> e1ea806e-3ecd-4827-adbe-2a76ab178d54
	 */
	public static String userIdFromXDIAddress(XDIAddress userIdXDIArc) {

		return userIdXDIArc.toString().startsWith("=!:uuid:") ? userIdXDIArc.toString().substring("=!:uuid:".length()) : null;
	}

	/**
	 * Maps a DiMe user ID to an XDI identifier.
	 * E.g. e1ea806e-3ecd-4827-adbe-2a76ab178d54 -> =!:uuid:e1ea806e-3ecd-4827-adbe-2a76ab178d54
	 */
	public static XDIAddress XDIAddressFromUserId(String userId) {

		return XDIAddress.create("=!:uuid:" + userId);
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
