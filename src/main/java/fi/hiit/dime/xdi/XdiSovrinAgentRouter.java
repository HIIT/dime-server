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
package fi.hiit.dime.xdi;

import java.net.URI;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import org.hyperledger.indy.sdk.ledger.Ledger;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonNull;
import com.google.gson.JsonObject;
import com.google.gson.JsonPrimitive;

import fi.hiit.dime.authentication.CurrentUser;
import fi.hiit.dime.authentication.User;
import fi.hiit.dime.data.Profile;
import fi.hiit.dime.sovrin.SovrinService;
import xdi2.agent.routing.XDIAgentRouter;
import xdi2.client.exceptions.Xdi2AgentException;
import xdi2.client.impl.http.XDIHttpClient;
import xdi2.client.impl.http.XDIHttpClientRoute;
import xdi2.core.features.nodetypes.XdiPeerRoot;
import xdi2.core.syntax.XDIArc;

public class XdiSovrinAgentRouter implements XDIAgentRouter<XDIHttpClientRoute, XDIHttpClient> {

    private static final Logger LOG =
        LoggerFactory.getLogger(XdiSovrinAgentRouter.class);

    public static final int RETRIES = 3;

    public static final Gson gson = new Gson();

    @Override
    public XDIHttpClientRoute route(XDIArc toPeerRootXDIArc) throws Xdi2AgentException {

        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        User user = ((CurrentUser) authentication.getPrincipal()).getUser();
        Profile profile = XdiService.get().profileDAO.profilesForUser(user.getId()).get(0);

        String submitterDid = XdiService.didStringFromXDIAddress(XdiService.getProfileDidXDIAddress(profile));
        String targetDid = XdiService.didStringFromXDIAddress(XdiPeerRoot.getXDIAddressOfPeerRootXDIArc(toPeerRootXDIArc));

        // GET_NYM request

        String indyRequest1 = null;
        String indyResult1 = null;

        try {

            for (int i=0; i<RETRIES; i++) {

                try {

                    indyRequest1 = Ledger.buildGetNymRequest(submitterDid, targetDid).get(5, TimeUnit.SECONDS);
                    LOG.info("Retry #" + i + ": Success: " + indyRequest1);
                    break;
                } catch (TimeoutException ex) {

                    LOG.warn("Retry #" + i + ": " + ex.getMessage());
                    if (i+1 < RETRIES) continue; else throw ex;
                }
            }

            for (int i=0; i<RETRIES; i++) {

                try {

                    indyResult1 = Ledger.signAndSubmitRequest(SovrinService.get().getPool(), SovrinService.get().getWallet(), submitterDid, indyRequest1).get(5, TimeUnit.SECONDS);
                    LOG.info("Retry #" + i + ": Success: " + indyResult1);
                    break;
                } catch (TimeoutException ex) {

                    LOG.warn("Retry #" + i + ": " + ex.getMessage());
                    if (i+1 < RETRIES) continue; else throw ex;
                }
            }
        } catch (Exception ex) {

            throw new RuntimeException("Cannot execute GET_NYM in Sovrin: " + ex.getMessage(), ex);
        }

        // GET_ATTR request

        String indyRequest2 = null;
        String indyResult2 = null;

        try {

            for (int i=0; i<RETRIES; i++) {

                try {

                    indyRequest2 = Ledger.buildGetAttribRequest(submitterDid, targetDid, "endpoint").get(5, TimeUnit.SECONDS);;
                    LOG.info("Retry #" + i + ": Success: " + indyRequest2);
                    break;
                } catch (TimeoutException ex) {

                    LOG.warn("Retry #" + i + ": " + ex.getMessage());
                    if (i+1 < RETRIES) continue; else throw ex;
                }
            }

            for (int i=0; i<RETRIES; i++) {

                try {

                    indyResult2 = Ledger.signAndSubmitRequest(SovrinService.get().getPool(), SovrinService.get().getWallet(), submitterDid, indyRequest2).get(5, TimeUnit.SECONDS);
                    LOG.info("Retry #" + i + ": Success: " + indyResult2);
                    break;
                } catch (TimeoutException ex) {

                    LOG.warn("Retry #" + i + ": " + ex.getMessage());
                    if (i+1 < RETRIES) continue; else throw ex;
                }
            }
        } catch (Exception ex) {

            throw new RuntimeException("Cannot execute GET_ATTR in Sovrin: " + ex.getMessage(), ex);
        }

        // result data

        JsonObject jsonReply2 = gson.fromJson(indyResult2, JsonObject.class);

        JsonObject result2 = jsonReply2 == null ? null : jsonReply2.getAsJsonObject("result");
        JsonElement dataString2 = result2 == null ? null : result2.get("data");
        JsonObject data2 = (dataString2 == null || dataString2 instanceof JsonNull) ? null : gson.fromJson(dataString2.getAsString(), JsonObject.class);

        // extract XDI endpoint URI

        JsonObject endpointJsonObject = data2 == null ? null : data2.getAsJsonObject("endpoint");
        JsonPrimitive xdiEndpointJsonElement = endpointJsonObject == null ? null : endpointJsonObject.getAsJsonPrimitive("xdi");
        String xdiEndpoint = xdiEndpointJsonElement == null ? null : xdiEndpointJsonElement.getAsString();

        // return XDI route

        return new XDIHttpClientRoute(toPeerRootXDIArc, URI.create(xdiEndpoint));
    }
}
