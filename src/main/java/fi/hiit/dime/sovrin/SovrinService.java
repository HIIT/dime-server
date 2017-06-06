package fi.hiit.dime.sovrin;

import java.io.File;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Service;

import com.danubetech.libsovrin.LibSovrin;
import com.danubetech.libsovrin.pool.Pool;
import com.danubetech.libsovrin.pool.PoolJSONParameters.CreatePoolLedgerConfigJSONParameter;
import com.danubetech.libsovrin.pool.PoolJSONParameters.OpenPoolLedgerJSONParameter;
import com.danubetech.libsovrin.pool.PoolResults.CreatePoolLedgerConfigResult;
import com.danubetech.libsovrin.pool.PoolResults.OpenPoolLedgerResult;
import com.danubetech.libsovrin.signus.Signus;
import com.danubetech.libsovrin.signus.SignusJSONParameters.CreateAndStoreMyDidJSONParameter;
import com.danubetech.libsovrin.signus.SignusResults.CreateAndStoreMyDidResult;
import com.danubetech.libsovrin.wallet.Wallet;
import com.danubetech.libsovrin.wallet.WalletResults.CreateWalletResult;
import com.danubetech.libsovrin.wallet.WalletResults.OpenWalletResult;

@Service
@Scope("singleton")
public class SovrinService {

	private static final Logger LOG = LoggerFactory.getLogger(SovrinService.class);

	private static SovrinService instance = null;

	public static final String TRUSTEE_DID = "V4SGRU86Z58d6TV7PBUe6f";
	public static final String TRUSTEE_VERKEY = "GJ1SzoWzavQYfNL9XkaJdrQejfztN4XqdsiV4ct3LXKL";
	public static final String TRUSTEE_SEED = "000000000000000000000000Trustee1";

	private Pool pool;
	private Wallet wallet;

	public static SovrinService get() {

		return instance;
	}

	public SovrinService() {

		LOG.debug("Initializing...");

		instance = this;

		String poolLedgerConfigName = "11347-04";
		String walletName = "trusteewallet";

		try {

			LOG.info("Loading libsovrin: " + new File("./lib/libsovrin.so").getAbsolutePath());
			if (! LibSovrin.isInitialized()) LibSovrin.init(new File("./lib/libsovrin.so"));
		} catch (Throwable ex) {

			LOG.warn(ex.getMessage(), ex);
		}

		if (! LibSovrin.isInitialized()) LibSovrin.init();

		// create pool

		try {

			CreatePoolLedgerConfigJSONParameter createPoolLedgerConfigJSONParameter = new CreatePoolLedgerConfigJSONParameter(poolLedgerConfigName + ".txn");
			CreatePoolLedgerConfigResult createPoolLedgerConfigResult = Pool.createPoolLedgerConfig(poolLedgerConfigName, createPoolLedgerConfigJSONParameter).get();
			LOG.info("Created pool: " + createPoolLedgerConfigResult);
		} catch (Exception ex) {

			LOG.warn("Cannot create pool: " + ex.getMessage());
		}

		// create wallet

		try {

			CreateWalletResult createWalletResultTrustee = Wallet.createWallet(poolLedgerConfigName, walletName, "default", null, null).get();
			LOG.info("Created wallet: " + createWalletResultTrustee);
		} catch (Exception ex) {

			LOG.warn("Cannot create wallet: " + ex.getMessage());
		}

		// open pool

		try {

			LOG.debug("Opening pool...");
			OpenPoolLedgerJSONParameter openPoolLedgerJSONParameter = new OpenPoolLedgerJSONParameter(Boolean.TRUE, null, null);
			OpenPoolLedgerResult openPoolLedgerResult = Pool.openPoolLedger(poolLedgerConfigName, openPoolLedgerJSONParameter).get();
			LOG.debug("Opened pool: " + openPoolLedgerResult);

			pool = openPoolLedgerResult.getPool();
		} catch (Exception ex) {

			throw new RuntimeException("Cannot open pool: " + ex.getMessage(), ex);
		}

		// open wallet

		try {

			LOG.debug("Opening wallet...");
			OpenWalletResult openWalletResult = Wallet.openWallet(walletName, null, null).get();
			LOG.debug("Opening wallet: " + openWalletResult);

			wallet = openWalletResult.getWallet();
		} catch (Exception ex) {

			throw new RuntimeException("Cannot open wallet: " + ex.getMessage(), ex);
		}

		// create trustee DID

		try {

			CreateAndStoreMyDidJSONParameter createAndStoreMyDidJSONParameterTrustee = new CreateAndStoreMyDidJSONParameter(null, TRUSTEE_SEED, null, null);
			CreateAndStoreMyDidResult createAndStoreMyDidResultTrustee = Signus.createAndStoreMyDid(wallet, createAndStoreMyDidJSONParameterTrustee).get();
			LOG.info("Created trustee DID: " + createAndStoreMyDidResultTrustee);
		} catch (Exception ex) {

			throw new RuntimeException("Cannot open pool: " + ex.getMessage(), ex);
		}
	}

	public Pool getPool() {

		return this.pool;
	}

	public Wallet getWallet() {

		return this.wallet;
	}
}
