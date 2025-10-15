package com.foodnutrition.app;

import androidx.annotation.NonNull;
import androidx.room.DatabaseConfiguration;
import androidx.room.InvalidationTracker;
import androidx.room.RoomDatabase;
import androidx.room.RoomOpenHelper;
import androidx.room.migration.AutoMigrationSpec;
import androidx.room.migration.Migration;
import androidx.room.util.DBUtil;
import androidx.room.util.TableInfo;
import androidx.sqlite.db.SupportSQLiteDatabase;
import androidx.sqlite.db.SupportSQLiteOpenHelper;
import java.lang.Class;
import java.lang.Override;
import java.lang.String;
import java.lang.SuppressWarnings;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import javax.annotation.processing.Generated;

@Generated("androidx.room.RoomProcessor")
@SuppressWarnings({"unchecked", "deprecation"})
public final class AppDatabase_Impl extends AppDatabase {
  private volatile ProductDao _productDao;

  @Override
  @NonNull
  protected SupportSQLiteOpenHelper createOpenHelper(@NonNull final DatabaseConfiguration config) {
    final SupportSQLiteOpenHelper.Callback _openCallback = new RoomOpenHelper(config, new RoomOpenHelper.Delegate(2) {
      @Override
      public void createAllTables(@NonNull final SupportSQLiteDatabase db) {
        db.execSQL("CREATE TABLE IF NOT EXISTS `products` (`id` TEXT NOT NULL, `product_name` TEXT NOT NULL, `brand` TEXT NOT NULL, `category` TEXT NOT NULL, `subcategory` TEXT, `size_value` REAL, `size_unit` TEXT, `price` REAL, `source` TEXT NOT NULL, `source_url` TEXT, `ingredients` TEXT, `image_url` TEXT, `last_updated` TEXT, `search_count` INTEGER NOT NULL, `llm_fallback_used` INTEGER NOT NULL, `data_quality_score` INTEGER NOT NULL, `available` INTEGER NOT NULL, `standardUnit` TEXT NOT NULL, `nutritionSource` TEXT NOT NULL, `lastChecked` INTEGER, `version` INTEGER NOT NULL, `createdAt` INTEGER NOT NULL, `updatedAt` INTEGER NOT NULL, `firebase_uploaded` INTEGER NOT NULL, PRIMARY KEY(`id`))");
        db.execSQL("CREATE TABLE IF NOT EXISTS room_master_table (id INTEGER PRIMARY KEY,identity_hash TEXT)");
        db.execSQL("INSERT OR REPLACE INTO room_master_table (id,identity_hash) VALUES(42, 'fdbcb1a0d4348be142617b2b2fc25563')");
      }

      @Override
      public void dropAllTables(@NonNull final SupportSQLiteDatabase db) {
        db.execSQL("DROP TABLE IF EXISTS `products`");
        final List<? extends RoomDatabase.Callback> _callbacks = mCallbacks;
        if (_callbacks != null) {
          for (RoomDatabase.Callback _callback : _callbacks) {
            _callback.onDestructiveMigration(db);
          }
        }
      }

      @Override
      public void onCreate(@NonNull final SupportSQLiteDatabase db) {
        final List<? extends RoomDatabase.Callback> _callbacks = mCallbacks;
        if (_callbacks != null) {
          for (RoomDatabase.Callback _callback : _callbacks) {
            _callback.onCreate(db);
          }
        }
      }

      @Override
      public void onOpen(@NonNull final SupportSQLiteDatabase db) {
        mDatabase = db;
        internalInitInvalidationTracker(db);
        final List<? extends RoomDatabase.Callback> _callbacks = mCallbacks;
        if (_callbacks != null) {
          for (RoomDatabase.Callback _callback : _callbacks) {
            _callback.onOpen(db);
          }
        }
      }

      @Override
      public void onPreMigrate(@NonNull final SupportSQLiteDatabase db) {
        DBUtil.dropFtsSyncTriggers(db);
      }

      @Override
      public void onPostMigrate(@NonNull final SupportSQLiteDatabase db) {
      }

      @Override
      @NonNull
      public RoomOpenHelper.ValidationResult onValidateSchema(
          @NonNull final SupportSQLiteDatabase db) {
        final HashMap<String, TableInfo.Column> _columnsProducts = new HashMap<String, TableInfo.Column>(24);
        _columnsProducts.put("id", new TableInfo.Column("id", "TEXT", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("product_name", new TableInfo.Column("product_name", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("brand", new TableInfo.Column("brand", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("category", new TableInfo.Column("category", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("subcategory", new TableInfo.Column("subcategory", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("size_value", new TableInfo.Column("size_value", "REAL", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("size_unit", new TableInfo.Column("size_unit", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("price", new TableInfo.Column("price", "REAL", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("source", new TableInfo.Column("source", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("source_url", new TableInfo.Column("source_url", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("ingredients", new TableInfo.Column("ingredients", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("image_url", new TableInfo.Column("image_url", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("last_updated", new TableInfo.Column("last_updated", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("search_count", new TableInfo.Column("search_count", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("llm_fallback_used", new TableInfo.Column("llm_fallback_used", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("data_quality_score", new TableInfo.Column("data_quality_score", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("available", new TableInfo.Column("available", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("standardUnit", new TableInfo.Column("standardUnit", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("nutritionSource", new TableInfo.Column("nutritionSource", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("lastChecked", new TableInfo.Column("lastChecked", "INTEGER", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("version", new TableInfo.Column("version", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("createdAt", new TableInfo.Column("createdAt", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("updatedAt", new TableInfo.Column("updatedAt", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsProducts.put("firebase_uploaded", new TableInfo.Column("firebase_uploaded", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysProducts = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesProducts = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoProducts = new TableInfo("products", _columnsProducts, _foreignKeysProducts, _indicesProducts);
        final TableInfo _existingProducts = TableInfo.read(db, "products");
        if (!_infoProducts.equals(_existingProducts)) {
          return new RoomOpenHelper.ValidationResult(false, "products(com.foodnutrition.app.Product).\n"
                  + " Expected:\n" + _infoProducts + "\n"
                  + " Found:\n" + _existingProducts);
        }
        return new RoomOpenHelper.ValidationResult(true, null);
      }
    }, "fdbcb1a0d4348be142617b2b2fc25563", "154b68f7beee6405943e119b3f29e312");
    final SupportSQLiteOpenHelper.Configuration _sqliteConfig = SupportSQLiteOpenHelper.Configuration.builder(config.context).name(config.name).callback(_openCallback).build();
    final SupportSQLiteOpenHelper _helper = config.sqliteOpenHelperFactory.create(_sqliteConfig);
    return _helper;
  }

  @Override
  @NonNull
  protected InvalidationTracker createInvalidationTracker() {
    final HashMap<String, String> _shadowTablesMap = new HashMap<String, String>(0);
    final HashMap<String, Set<String>> _viewTables = new HashMap<String, Set<String>>(0);
    return new InvalidationTracker(this, _shadowTablesMap, _viewTables, "products");
  }

  @Override
  public void clearAllTables() {
    super.assertNotMainThread();
    final SupportSQLiteDatabase _db = super.getOpenHelper().getWritableDatabase();
    try {
      super.beginTransaction();
      _db.execSQL("DELETE FROM `products`");
      super.setTransactionSuccessful();
    } finally {
      super.endTransaction();
      _db.query("PRAGMA wal_checkpoint(FULL)").close();
      if (!_db.inTransaction()) {
        _db.execSQL("VACUUM");
      }
    }
  }

  @Override
  @NonNull
  protected Map<Class<?>, List<Class<?>>> getRequiredTypeConverters() {
    final HashMap<Class<?>, List<Class<?>>> _typeConvertersMap = new HashMap<Class<?>, List<Class<?>>>();
    _typeConvertersMap.put(ProductDao.class, ProductDao_Impl.getRequiredConverters());
    return _typeConvertersMap;
  }

  @Override
  @NonNull
  public Set<Class<? extends AutoMigrationSpec>> getRequiredAutoMigrationSpecs() {
    final HashSet<Class<? extends AutoMigrationSpec>> _autoMigrationSpecsSet = new HashSet<Class<? extends AutoMigrationSpec>>();
    return _autoMigrationSpecsSet;
  }

  @Override
  @NonNull
  public List<Migration> getAutoMigrations(
      @NonNull final Map<Class<? extends AutoMigrationSpec>, AutoMigrationSpec> autoMigrationSpecs) {
    final List<Migration> _autoMigrations = new ArrayList<Migration>();
    return _autoMigrations;
  }

  @Override
  public ProductDao productDao() {
    if (_productDao != null) {
      return _productDao;
    } else {
      synchronized(this) {
        if(_productDao == null) {
          _productDao = new ProductDao_Impl(this);
        }
        return _productDao;
      }
    }
  }
}
