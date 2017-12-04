package fi.hiit.dime.sovrin;

import java.io.File;

import org.hyperledger.indy.sdk.LibIndy;
import org.hyperledger.indy.sdk.pool.Pool;
import org.hyperledger.indy.sdk.pool.PoolJSONParameters.CreatePoolLedgerConfigJSONParameter;
import org.hyperledger.indy.sdk.pool.PoolJSONParameters.OpenPoolLedgerJSONParameter;
import org.hyperledger.indy.sdk.signus.Signus;
import org.hyperledger.indy.sdk.signus.SignusJSONParameters.CreateAndStoreMyDidJSONParameter;
import org.hyperledger.indy.sdk.signus.SignusResults.CreateAndStoreMyDidResult;
import org.hyperledger.indy.sdk.wallet.Wallet;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Service;

import fi.hiit.dime.DiMeProperties;

@Service
@Scope("singleton")
public class SovrinService {

	private static final Logger LOG = LoggerFactory.getLogger(SovrinService.class);

	private static SovrinService instance = null;

	public static final String TRUSTEE_DID = "V4SGRU86Z58d6TV7PBUe6f";
	public static final String TRUSTEE_VERKEY = "GJ1SzoWzavQYfNL9XkaJdrQejfztN4XqdsiV4ct3LXKL";
	public static final String TRUSTEE_SEED = "000000000000000000000000Trustee1";

	private Pool pool = null;
	private Wallet wallet = null;

	private final DiMeProperties dimeConfig;

	public static SovrinService get() {

		return instance;
	}

	@Autowired
	public SovrinService(DiMeProperties dimeConfig) {
		this.dimeConfig = dimeConfig;

		LOG.debug("Initializing...");

		instance = this;

		String poolLedgerConfigName = dimeConfig.getSovrinPoolConfig();
		String walletName = "dimewallet";

                if (poolLedgerConfigName == null) {
                    return;
                }

		try {

			LOG.info("Loading libindy: " + new File("lib/libindy.so").getAbsolutePath());
			if (! LibIndy.isInitialized()) LibIndy.init(new File("lib/libindy.so"));
		} catch (Throwable ex) {

			LOG.warn(ex.getMessage(), ex);
		}

		if (! LibIndy.isInitialized()) LibIndy.init();

		// create pool

		try {

			CreatePoolLedgerConfigJSONParameter createPoolLedgerConfigJSONParameter = new CreatePoolLedgerConfigJSONParameter(poolLedgerConfigName + ".txn");
			Pool.createPoolLedgerConfig(poolLedgerConfigName, createPoolLedgerConfigJSONParameter.toJson()).get();
			LOG.info("Created pool.");
		} catch (Exception ex) {

			LOG.warn("Cannot create pool: " + ex.getMessage());
		}

		// create wallet

		try {

			Wallet.createWallet(poolLedgerConfigName, walletName, "default", null, null).get();
			LOG.info("Created wallet.");
		} catch (Exception ex) {

			LOG.warn("Cannot create wallet: " + ex.getMessage());
		}

		// open pool

		try {

			LOG.debug("Opening pool...");
			OpenPoolLedgerJSONParameter openPoolLedgerJSONParameter = new OpenPoolLedgerJSONParameter(Boolean.TRUE, null, null);
			pool = Pool.openPoolLedger(poolLedgerConfigName, openPoolLedgerJSONParameter.toJson()).get();
			LOG.debug("Opened pool: " + pool);
		} catch (Exception ex) {

			throw new RuntimeException("Cannot open pool: " + ex.getMessage(), ex);
		}

		// open wallet

		try {

			LOG.debug("Opening wallet...");
			wallet = Wallet.openWallet(walletName, null, null).get();
			LOG.debug("Opening wallet: " + wallet);
		} catch (Exception ex) {

			throw new RuntimeException("Cannot open wallet: " + ex.getMessage(), ex);
		}

		// create trustee DID
		if (dimeConfig.getSovrinSelfRegisteringDID()) {
			try {
				CreateAndStoreMyDidJSONParameter createAndStoreMyDidJSONParameterTrustee = new CreateAndStoreMyDidJSONParameter(null, TRUSTEE_SEED, null, null);
				CreateAndStoreMyDidResult createAndStoreMyDidResultTrustee = Signus.createAndStoreMyDid(wallet, createAndStoreMyDidJSONParameterTrustee.toJson()).get();
				LOG.info("Created trustee DID: " + createAndStoreMyDidResultTrustee);
			} catch (Exception ex) {
				throw new RuntimeException("Cannot open pool: " + ex.getMessage(), ex);
			}
		}
	}

	public Pool getPool() {

		return this.pool;
	}

	public Wallet getWallet() {

		return this.wallet;
	}
}
