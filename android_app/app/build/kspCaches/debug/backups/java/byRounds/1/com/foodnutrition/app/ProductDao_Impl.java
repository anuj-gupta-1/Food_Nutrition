package com.foodnutrition.app;

import android.database.Cursor;
import android.os.CancellationSignal;
import androidx.annotation.NonNull;
import androidx.room.CoroutinesRoom;
import androidx.room.EntityInsertionAdapter;
import androidx.room.RoomDatabase;
import androidx.room.RoomSQLiteQuery;
import androidx.room.SharedSQLiteStatement;
import androidx.room.util.CursorUtil;
import androidx.room.util.DBUtil;
import androidx.sqlite.db.SupportSQLiteStatement;
import java.lang.Class;
import java.lang.Double;
import java.lang.Exception;
import java.lang.Integer;
import java.lang.Long;
import java.lang.Object;
import java.lang.Override;
import java.lang.String;
import java.lang.SuppressWarnings;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Callable;
import javax.annotation.processing.Generated;
import kotlin.Unit;
import kotlin.coroutines.Continuation;
import kotlinx.coroutines.flow.Flow;

@Generated("androidx.room.RoomProcessor")
@SuppressWarnings({"unchecked", "deprecation"})
public final class ProductDao_Impl implements ProductDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<Product> __insertionAdapterOfProduct;

  private final SharedSQLiteStatement __preparedStmtOfDeleteAll;

  public ProductDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfProduct = new EntityInsertionAdapter<Product>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `products` (`id`,`product_name`,`brand`,`category`,`subcategory`,`size_value`,`size_unit`,`price`,`source`,`source_url`,`ingredients`,`image_url`,`last_updated`,`search_count`,`llm_fallback_used`,`data_quality_score`,`available`,`standardUnit`,`nutritionSource`,`lastChecked`,`version`,`createdAt`,`updatedAt`,`firebase_uploaded`) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final Product entity) {
        statement.bindString(1, entity.getId());
        statement.bindString(2, entity.getProduct_name());
        statement.bindString(3, entity.getBrand());
        statement.bindString(4, entity.getCategory());
        if (entity.getSubcategory() == null) {
          statement.bindNull(5);
        } else {
          statement.bindString(5, entity.getSubcategory());
        }
        if (entity.getSize_value() == null) {
          statement.bindNull(6);
        } else {
          statement.bindDouble(6, entity.getSize_value());
        }
        if (entity.getSize_unit() == null) {
          statement.bindNull(7);
        } else {
          statement.bindString(7, entity.getSize_unit());
        }
        if (entity.getPrice() == null) {
          statement.bindNull(8);
        } else {
          statement.bindDouble(8, entity.getPrice());
        }
        statement.bindString(9, entity.getSource());
        if (entity.getSource_url() == null) {
          statement.bindNull(10);
        } else {
          statement.bindString(10, entity.getSource_url());
        }
        if (entity.getIngredients() == null) {
          statement.bindNull(11);
        } else {
          statement.bindString(11, entity.getIngredients());
        }
        if (entity.getImage_url() == null) {
          statement.bindNull(12);
        } else {
          statement.bindString(12, entity.getImage_url());
        }
        if (entity.getLast_updated() == null) {
          statement.bindNull(13);
        } else {
          statement.bindString(13, entity.getLast_updated());
        }
        statement.bindLong(14, entity.getSearch_count());
        final int _tmp = entity.getLlm_fallback_used() ? 1 : 0;
        statement.bindLong(15, _tmp);
        statement.bindLong(16, entity.getData_quality_score());
        final NutritionData _tmpNutrition_data = entity.getNutrition_data();
        final int _tmp_1 = _tmpNutrition_data.getAvailable() ? 1 : 0;
        statement.bindLong(17, _tmp_1);
        statement.bindString(18, _tmpNutrition_data.getStandardUnit());
        statement.bindString(19, _tmpNutrition_data.getNutritionSource());
        if (_tmpNutrition_data.getLastChecked() == null) {
          statement.bindNull(20);
        } else {
          statement.bindLong(20, _tmpNutrition_data.getLastChecked());
        }
        final ProductMetadata _tmpMetadata = entity.getMetadata();
        statement.bindLong(21, _tmpMetadata.getVersion());
        statement.bindLong(22, _tmpMetadata.getCreatedAt());
        statement.bindLong(23, _tmpMetadata.getUpdatedAt());
        final int _tmp_2 = _tmpMetadata.getFirebase_uploaded() ? 1 : 0;
        statement.bindLong(24, _tmp_2);
      }
    };
    this.__preparedStmtOfDeleteAll = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "DELETE FROM products";
        return _query;
      }
    };
  }

  @Override
  public Object insertAll(final List<Product> products,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfProduct.insert(products);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object deleteAll(final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        final SupportSQLiteStatement _stmt = __preparedStmtOfDeleteAll.acquire();
        try {
          __db.beginTransaction();
          try {
            _stmt.executeUpdateDelete();
            __db.setTransactionSuccessful();
            return Unit.INSTANCE;
          } finally {
            __db.endTransaction();
          }
        } finally {
          __preparedStmtOfDeleteAll.release(_stmt);
        }
      }
    }, $completion);
  }

  @Override
  public Flow<List<Product>> getProductsByCategory(final String category) {
    final String _sql = "SELECT * FROM products WHERE category = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, category);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"products"}, new Callable<List<Product>>() {
      @Override
      @NonNull
      public List<Product> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfProductName = CursorUtil.getColumnIndexOrThrow(_cursor, "product_name");
          final int _cursorIndexOfBrand = CursorUtil.getColumnIndexOrThrow(_cursor, "brand");
          final int _cursorIndexOfCategory = CursorUtil.getColumnIndexOrThrow(_cursor, "category");
          final int _cursorIndexOfSubcategory = CursorUtil.getColumnIndexOrThrow(_cursor, "subcategory");
          final int _cursorIndexOfSizeValue = CursorUtil.getColumnIndexOrThrow(_cursor, "size_value");
          final int _cursorIndexOfSizeUnit = CursorUtil.getColumnIndexOrThrow(_cursor, "size_unit");
          final int _cursorIndexOfPrice = CursorUtil.getColumnIndexOrThrow(_cursor, "price");
          final int _cursorIndexOfSource = CursorUtil.getColumnIndexOrThrow(_cursor, "source");
          final int _cursorIndexOfSourceUrl = CursorUtil.getColumnIndexOrThrow(_cursor, "source_url");
          final int _cursorIndexOfIngredients = CursorUtil.getColumnIndexOrThrow(_cursor, "ingredients");
          final int _cursorIndexOfImageUrl = CursorUtil.getColumnIndexOrThrow(_cursor, "image_url");
          final int _cursorIndexOfLastUpdated = CursorUtil.getColumnIndexOrThrow(_cursor, "last_updated");
          final int _cursorIndexOfSearchCount = CursorUtil.getColumnIndexOrThrow(_cursor, "search_count");
          final int _cursorIndexOfLlmFallbackUsed = CursorUtil.getColumnIndexOrThrow(_cursor, "llm_fallback_used");
          final int _cursorIndexOfDataQualityScore = CursorUtil.getColumnIndexOrThrow(_cursor, "data_quality_score");
          final int _cursorIndexOfAvailable = CursorUtil.getColumnIndexOrThrow(_cursor, "available");
          final int _cursorIndexOfStandardUnit = CursorUtil.getColumnIndexOrThrow(_cursor, "standardUnit");
          final int _cursorIndexOfNutritionSource = CursorUtil.getColumnIndexOrThrow(_cursor, "nutritionSource");
          final int _cursorIndexOfLastChecked = CursorUtil.getColumnIndexOrThrow(_cursor, "lastChecked");
          final int _cursorIndexOfVersion = CursorUtil.getColumnIndexOrThrow(_cursor, "version");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final int _cursorIndexOfUpdatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "updatedAt");
          final int _cursorIndexOfFirebaseUploaded = CursorUtil.getColumnIndexOrThrow(_cursor, "firebase_uploaded");
          final List<Product> _result = new ArrayList<Product>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final Product _item;
            final String _tmpId;
            _tmpId = _cursor.getString(_cursorIndexOfId);
            final String _tmpProduct_name;
            _tmpProduct_name = _cursor.getString(_cursorIndexOfProductName);
            final String _tmpBrand;
            _tmpBrand = _cursor.getString(_cursorIndexOfBrand);
            final String _tmpCategory;
            _tmpCategory = _cursor.getString(_cursorIndexOfCategory);
            final String _tmpSubcategory;
            if (_cursor.isNull(_cursorIndexOfSubcategory)) {
              _tmpSubcategory = null;
            } else {
              _tmpSubcategory = _cursor.getString(_cursorIndexOfSubcategory);
            }
            final Double _tmpSize_value;
            if (_cursor.isNull(_cursorIndexOfSizeValue)) {
              _tmpSize_value = null;
            } else {
              _tmpSize_value = _cursor.getDouble(_cursorIndexOfSizeValue);
            }
            final String _tmpSize_unit;
            if (_cursor.isNull(_cursorIndexOfSizeUnit)) {
              _tmpSize_unit = null;
            } else {
              _tmpSize_unit = _cursor.getString(_cursorIndexOfSizeUnit);
            }
            final Double _tmpPrice;
            if (_cursor.isNull(_cursorIndexOfPrice)) {
              _tmpPrice = null;
            } else {
              _tmpPrice = _cursor.getDouble(_cursorIndexOfPrice);
            }
            final String _tmpSource;
            _tmpSource = _cursor.getString(_cursorIndexOfSource);
            final String _tmpSource_url;
            if (_cursor.isNull(_cursorIndexOfSourceUrl)) {
              _tmpSource_url = null;
            } else {
              _tmpSource_url = _cursor.getString(_cursorIndexOfSourceUrl);
            }
            final String _tmpIngredients;
            if (_cursor.isNull(_cursorIndexOfIngredients)) {
              _tmpIngredients = null;
            } else {
              _tmpIngredients = _cursor.getString(_cursorIndexOfIngredients);
            }
            final String _tmpImage_url;
            if (_cursor.isNull(_cursorIndexOfImageUrl)) {
              _tmpImage_url = null;
            } else {
              _tmpImage_url = _cursor.getString(_cursorIndexOfImageUrl);
            }
            final String _tmpLast_updated;
            if (_cursor.isNull(_cursorIndexOfLastUpdated)) {
              _tmpLast_updated = null;
            } else {
              _tmpLast_updated = _cursor.getString(_cursorIndexOfLastUpdated);
            }
            final int _tmpSearch_count;
            _tmpSearch_count = _cursor.getInt(_cursorIndexOfSearchCount);
            final boolean _tmpLlm_fallback_used;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfLlmFallbackUsed);
            _tmpLlm_fallback_used = _tmp != 0;
            final int _tmpData_quality_score;
            _tmpData_quality_score = _cursor.getInt(_cursorIndexOfDataQualityScore);
            final NutritionData _tmpNutrition_data;
            final boolean _tmpAvailable;
            final int _tmp_1;
            _tmp_1 = _cursor.getInt(_cursorIndexOfAvailable);
            _tmpAvailable = _tmp_1 != 0;
            final String _tmpStandardUnit;
            _tmpStandardUnit = _cursor.getString(_cursorIndexOfStandardUnit);
            final String _tmpNutritionSource;
            _tmpNutritionSource = _cursor.getString(_cursorIndexOfNutritionSource);
            final Long _tmpLastChecked;
            if (_cursor.isNull(_cursorIndexOfLastChecked)) {
              _tmpLastChecked = null;
            } else {
              _tmpLastChecked = _cursor.getLong(_cursorIndexOfLastChecked);
            }
            _tmpNutrition_data = new NutritionData(_tmpAvailable,_tmpStandardUnit,_tmpNutritionSource,_tmpLastChecked);
            final ProductMetadata _tmpMetadata;
            final int _tmpVersion;
            _tmpVersion = _cursor.getInt(_cursorIndexOfVersion);
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            final long _tmpUpdatedAt;
            _tmpUpdatedAt = _cursor.getLong(_cursorIndexOfUpdatedAt);
            final boolean _tmpFirebase_uploaded;
            final int _tmp_2;
            _tmp_2 = _cursor.getInt(_cursorIndexOfFirebaseUploaded);
            _tmpFirebase_uploaded = _tmp_2 != 0;
            _tmpMetadata = new ProductMetadata(_tmpVersion,_tmpCreatedAt,_tmpUpdatedAt,_tmpFirebase_uploaded);
            _item = new Product(_tmpId,_tmpProduct_name,_tmpBrand,_tmpCategory,_tmpSubcategory,_tmpSize_value,_tmpSize_unit,_tmpPrice,_tmpSource,_tmpSource_url,_tmpIngredients,_tmpNutrition_data,_tmpImage_url,_tmpLast_updated,_tmpSearch_count,_tmpLlm_fallback_used,_tmpData_quality_score,_tmpMetadata);
            _result.add(_item);
          }
          return _result;
        } finally {
          _cursor.close();
        }
      }

      @Override
      protected void finalize() {
        _statement.release();
      }
    });
  }

  @Override
  public Flow<List<Product>> searchProducts(final String query) {
    final String _sql = "SELECT * FROM products WHERE product_name LIKE '%' || ? || '%' OR brand LIKE '%' || ? || '%'";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 2);
    int _argIndex = 1;
    _statement.bindString(_argIndex, query);
    _argIndex = 2;
    _statement.bindString(_argIndex, query);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"products"}, new Callable<List<Product>>() {
      @Override
      @NonNull
      public List<Product> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfProductName = CursorUtil.getColumnIndexOrThrow(_cursor, "product_name");
          final int _cursorIndexOfBrand = CursorUtil.getColumnIndexOrThrow(_cursor, "brand");
          final int _cursorIndexOfCategory = CursorUtil.getColumnIndexOrThrow(_cursor, "category");
          final int _cursorIndexOfSubcategory = CursorUtil.getColumnIndexOrThrow(_cursor, "subcategory");
          final int _cursorIndexOfSizeValue = CursorUtil.getColumnIndexOrThrow(_cursor, "size_value");
          final int _cursorIndexOfSizeUnit = CursorUtil.getColumnIndexOrThrow(_cursor, "size_unit");
          final int _cursorIndexOfPrice = CursorUtil.getColumnIndexOrThrow(_cursor, "price");
          final int _cursorIndexOfSource = CursorUtil.getColumnIndexOrThrow(_cursor, "source");
          final int _cursorIndexOfSourceUrl = CursorUtil.getColumnIndexOrThrow(_cursor, "source_url");
          final int _cursorIndexOfIngredients = CursorUtil.getColumnIndexOrThrow(_cursor, "ingredients");
          final int _cursorIndexOfImageUrl = CursorUtil.getColumnIndexOrThrow(_cursor, "image_url");
          final int _cursorIndexOfLastUpdated = CursorUtil.getColumnIndexOrThrow(_cursor, "last_updated");
          final int _cursorIndexOfSearchCount = CursorUtil.getColumnIndexOrThrow(_cursor, "search_count");
          final int _cursorIndexOfLlmFallbackUsed = CursorUtil.getColumnIndexOrThrow(_cursor, "llm_fallback_used");
          final int _cursorIndexOfDataQualityScore = CursorUtil.getColumnIndexOrThrow(_cursor, "data_quality_score");
          final int _cursorIndexOfAvailable = CursorUtil.getColumnIndexOrThrow(_cursor, "available");
          final int _cursorIndexOfStandardUnit = CursorUtil.getColumnIndexOrThrow(_cursor, "standardUnit");
          final int _cursorIndexOfNutritionSource = CursorUtil.getColumnIndexOrThrow(_cursor, "nutritionSource");
          final int _cursorIndexOfLastChecked = CursorUtil.getColumnIndexOrThrow(_cursor, "lastChecked");
          final int _cursorIndexOfVersion = CursorUtil.getColumnIndexOrThrow(_cursor, "version");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final int _cursorIndexOfUpdatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "updatedAt");
          final int _cursorIndexOfFirebaseUploaded = CursorUtil.getColumnIndexOrThrow(_cursor, "firebase_uploaded");
          final List<Product> _result = new ArrayList<Product>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final Product _item;
            final String _tmpId;
            _tmpId = _cursor.getString(_cursorIndexOfId);
            final String _tmpProduct_name;
            _tmpProduct_name = _cursor.getString(_cursorIndexOfProductName);
            final String _tmpBrand;
            _tmpBrand = _cursor.getString(_cursorIndexOfBrand);
            final String _tmpCategory;
            _tmpCategory = _cursor.getString(_cursorIndexOfCategory);
            final String _tmpSubcategory;
            if (_cursor.isNull(_cursorIndexOfSubcategory)) {
              _tmpSubcategory = null;
            } else {
              _tmpSubcategory = _cursor.getString(_cursorIndexOfSubcategory);
            }
            final Double _tmpSize_value;
            if (_cursor.isNull(_cursorIndexOfSizeValue)) {
              _tmpSize_value = null;
            } else {
              _tmpSize_value = _cursor.getDouble(_cursorIndexOfSizeValue);
            }
            final String _tmpSize_unit;
            if (_cursor.isNull(_cursorIndexOfSizeUnit)) {
              _tmpSize_unit = null;
            } else {
              _tmpSize_unit = _cursor.getString(_cursorIndexOfSizeUnit);
            }
            final Double _tmpPrice;
            if (_cursor.isNull(_cursorIndexOfPrice)) {
              _tmpPrice = null;
            } else {
              _tmpPrice = _cursor.getDouble(_cursorIndexOfPrice);
            }
            final String _tmpSource;
            _tmpSource = _cursor.getString(_cursorIndexOfSource);
            final String _tmpSource_url;
            if (_cursor.isNull(_cursorIndexOfSourceUrl)) {
              _tmpSource_url = null;
            } else {
              _tmpSource_url = _cursor.getString(_cursorIndexOfSourceUrl);
            }
            final String _tmpIngredients;
            if (_cursor.isNull(_cursorIndexOfIngredients)) {
              _tmpIngredients = null;
            } else {
              _tmpIngredients = _cursor.getString(_cursorIndexOfIngredients);
            }
            final String _tmpImage_url;
            if (_cursor.isNull(_cursorIndexOfImageUrl)) {
              _tmpImage_url = null;
            } else {
              _tmpImage_url = _cursor.getString(_cursorIndexOfImageUrl);
            }
            final String _tmpLast_updated;
            if (_cursor.isNull(_cursorIndexOfLastUpdated)) {
              _tmpLast_updated = null;
            } else {
              _tmpLast_updated = _cursor.getString(_cursorIndexOfLastUpdated);
            }
            final int _tmpSearch_count;
            _tmpSearch_count = _cursor.getInt(_cursorIndexOfSearchCount);
            final boolean _tmpLlm_fallback_used;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfLlmFallbackUsed);
            _tmpLlm_fallback_used = _tmp != 0;
            final int _tmpData_quality_score;
            _tmpData_quality_score = _cursor.getInt(_cursorIndexOfDataQualityScore);
            final NutritionData _tmpNutrition_data;
            final boolean _tmpAvailable;
            final int _tmp_1;
            _tmp_1 = _cursor.getInt(_cursorIndexOfAvailable);
            _tmpAvailable = _tmp_1 != 0;
            final String _tmpStandardUnit;
            _tmpStandardUnit = _cursor.getString(_cursorIndexOfStandardUnit);
            final String _tmpNutritionSource;
            _tmpNutritionSource = _cursor.getString(_cursorIndexOfNutritionSource);
            final Long _tmpLastChecked;
            if (_cursor.isNull(_cursorIndexOfLastChecked)) {
              _tmpLastChecked = null;
            } else {
              _tmpLastChecked = _cursor.getLong(_cursorIndexOfLastChecked);
            }
            _tmpNutrition_data = new NutritionData(_tmpAvailable,_tmpStandardUnit,_tmpNutritionSource,_tmpLastChecked);
            final ProductMetadata _tmpMetadata;
            final int _tmpVersion;
            _tmpVersion = _cursor.getInt(_cursorIndexOfVersion);
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            final long _tmpUpdatedAt;
            _tmpUpdatedAt = _cursor.getLong(_cursorIndexOfUpdatedAt);
            final boolean _tmpFirebase_uploaded;
            final int _tmp_2;
            _tmp_2 = _cursor.getInt(_cursorIndexOfFirebaseUploaded);
            _tmpFirebase_uploaded = _tmp_2 != 0;
            _tmpMetadata = new ProductMetadata(_tmpVersion,_tmpCreatedAt,_tmpUpdatedAt,_tmpFirebase_uploaded);
            _item = new Product(_tmpId,_tmpProduct_name,_tmpBrand,_tmpCategory,_tmpSubcategory,_tmpSize_value,_tmpSize_unit,_tmpPrice,_tmpSource,_tmpSource_url,_tmpIngredients,_tmpNutrition_data,_tmpImage_url,_tmpLast_updated,_tmpSearch_count,_tmpLlm_fallback_used,_tmpData_quality_score,_tmpMetadata);
            _result.add(_item);
          }
          return _result;
        } finally {
          _cursor.close();
        }
      }

      @Override
      protected void finalize() {
        _statement.release();
      }
    });
  }

  @Override
  public Flow<List<Product>> getProductsBySource(final String source) {
    final String _sql = "SELECT * FROM products WHERE source = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, source);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"products"}, new Callable<List<Product>>() {
      @Override
      @NonNull
      public List<Product> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfProductName = CursorUtil.getColumnIndexOrThrow(_cursor, "product_name");
          final int _cursorIndexOfBrand = CursorUtil.getColumnIndexOrThrow(_cursor, "brand");
          final int _cursorIndexOfCategory = CursorUtil.getColumnIndexOrThrow(_cursor, "category");
          final int _cursorIndexOfSubcategory = CursorUtil.getColumnIndexOrThrow(_cursor, "subcategory");
          final int _cursorIndexOfSizeValue = CursorUtil.getColumnIndexOrThrow(_cursor, "size_value");
          final int _cursorIndexOfSizeUnit = CursorUtil.getColumnIndexOrThrow(_cursor, "size_unit");
          final int _cursorIndexOfPrice = CursorUtil.getColumnIndexOrThrow(_cursor, "price");
          final int _cursorIndexOfSource = CursorUtil.getColumnIndexOrThrow(_cursor, "source");
          final int _cursorIndexOfSourceUrl = CursorUtil.getColumnIndexOrThrow(_cursor, "source_url");
          final int _cursorIndexOfIngredients = CursorUtil.getColumnIndexOrThrow(_cursor, "ingredients");
          final int _cursorIndexOfImageUrl = CursorUtil.getColumnIndexOrThrow(_cursor, "image_url");
          final int _cursorIndexOfLastUpdated = CursorUtil.getColumnIndexOrThrow(_cursor, "last_updated");
          final int _cursorIndexOfSearchCount = CursorUtil.getColumnIndexOrThrow(_cursor, "search_count");
          final int _cursorIndexOfLlmFallbackUsed = CursorUtil.getColumnIndexOrThrow(_cursor, "llm_fallback_used");
          final int _cursorIndexOfDataQualityScore = CursorUtil.getColumnIndexOrThrow(_cursor, "data_quality_score");
          final int _cursorIndexOfAvailable = CursorUtil.getColumnIndexOrThrow(_cursor, "available");
          final int _cursorIndexOfStandardUnit = CursorUtil.getColumnIndexOrThrow(_cursor, "standardUnit");
          final int _cursorIndexOfNutritionSource = CursorUtil.getColumnIndexOrThrow(_cursor, "nutritionSource");
          final int _cursorIndexOfLastChecked = CursorUtil.getColumnIndexOrThrow(_cursor, "lastChecked");
          final int _cursorIndexOfVersion = CursorUtil.getColumnIndexOrThrow(_cursor, "version");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final int _cursorIndexOfUpdatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "updatedAt");
          final int _cursorIndexOfFirebaseUploaded = CursorUtil.getColumnIndexOrThrow(_cursor, "firebase_uploaded");
          final List<Product> _result = new ArrayList<Product>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final Product _item;
            final String _tmpId;
            _tmpId = _cursor.getString(_cursorIndexOfId);
            final String _tmpProduct_name;
            _tmpProduct_name = _cursor.getString(_cursorIndexOfProductName);
            final String _tmpBrand;
            _tmpBrand = _cursor.getString(_cursorIndexOfBrand);
            final String _tmpCategory;
            _tmpCategory = _cursor.getString(_cursorIndexOfCategory);
            final String _tmpSubcategory;
            if (_cursor.isNull(_cursorIndexOfSubcategory)) {
              _tmpSubcategory = null;
            } else {
              _tmpSubcategory = _cursor.getString(_cursorIndexOfSubcategory);
            }
            final Double _tmpSize_value;
            if (_cursor.isNull(_cursorIndexOfSizeValue)) {
              _tmpSize_value = null;
            } else {
              _tmpSize_value = _cursor.getDouble(_cursorIndexOfSizeValue);
            }
            final String _tmpSize_unit;
            if (_cursor.isNull(_cursorIndexOfSizeUnit)) {
              _tmpSize_unit = null;
            } else {
              _tmpSize_unit = _cursor.getString(_cursorIndexOfSizeUnit);
            }
            final Double _tmpPrice;
            if (_cursor.isNull(_cursorIndexOfPrice)) {
              _tmpPrice = null;
            } else {
              _tmpPrice = _cursor.getDouble(_cursorIndexOfPrice);
            }
            final String _tmpSource;
            _tmpSource = _cursor.getString(_cursorIndexOfSource);
            final String _tmpSource_url;
            if (_cursor.isNull(_cursorIndexOfSourceUrl)) {
              _tmpSource_url = null;
            } else {
              _tmpSource_url = _cursor.getString(_cursorIndexOfSourceUrl);
            }
            final String _tmpIngredients;
            if (_cursor.isNull(_cursorIndexOfIngredients)) {
              _tmpIngredients = null;
            } else {
              _tmpIngredients = _cursor.getString(_cursorIndexOfIngredients);
            }
            final String _tmpImage_url;
            if (_cursor.isNull(_cursorIndexOfImageUrl)) {
              _tmpImage_url = null;
            } else {
              _tmpImage_url = _cursor.getString(_cursorIndexOfImageUrl);
            }
            final String _tmpLast_updated;
            if (_cursor.isNull(_cursorIndexOfLastUpdated)) {
              _tmpLast_updated = null;
            } else {
              _tmpLast_updated = _cursor.getString(_cursorIndexOfLastUpdated);
            }
            final int _tmpSearch_count;
            _tmpSearch_count = _cursor.getInt(_cursorIndexOfSearchCount);
            final boolean _tmpLlm_fallback_used;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfLlmFallbackUsed);
            _tmpLlm_fallback_used = _tmp != 0;
            final int _tmpData_quality_score;
            _tmpData_quality_score = _cursor.getInt(_cursorIndexOfDataQualityScore);
            final NutritionData _tmpNutrition_data;
            final boolean _tmpAvailable;
            final int _tmp_1;
            _tmp_1 = _cursor.getInt(_cursorIndexOfAvailable);
            _tmpAvailable = _tmp_1 != 0;
            final String _tmpStandardUnit;
            _tmpStandardUnit = _cursor.getString(_cursorIndexOfStandardUnit);
            final String _tmpNutritionSource;
            _tmpNutritionSource = _cursor.getString(_cursorIndexOfNutritionSource);
            final Long _tmpLastChecked;
            if (_cursor.isNull(_cursorIndexOfLastChecked)) {
              _tmpLastChecked = null;
            } else {
              _tmpLastChecked = _cursor.getLong(_cursorIndexOfLastChecked);
            }
            _tmpNutrition_data = new NutritionData(_tmpAvailable,_tmpStandardUnit,_tmpNutritionSource,_tmpLastChecked);
            final ProductMetadata _tmpMetadata;
            final int _tmpVersion;
            _tmpVersion = _cursor.getInt(_cursorIndexOfVersion);
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            final long _tmpUpdatedAt;
            _tmpUpdatedAt = _cursor.getLong(_cursorIndexOfUpdatedAt);
            final boolean _tmpFirebase_uploaded;
            final int _tmp_2;
            _tmp_2 = _cursor.getInt(_cursorIndexOfFirebaseUploaded);
            _tmpFirebase_uploaded = _tmp_2 != 0;
            _tmpMetadata = new ProductMetadata(_tmpVersion,_tmpCreatedAt,_tmpUpdatedAt,_tmpFirebase_uploaded);
            _item = new Product(_tmpId,_tmpProduct_name,_tmpBrand,_tmpCategory,_tmpSubcategory,_tmpSize_value,_tmpSize_unit,_tmpPrice,_tmpSource,_tmpSource_url,_tmpIngredients,_tmpNutrition_data,_tmpImage_url,_tmpLast_updated,_tmpSearch_count,_tmpLlm_fallback_used,_tmpData_quality_score,_tmpMetadata);
            _result.add(_item);
          }
          return _result;
        } finally {
          _cursor.close();
        }
      }

      @Override
      protected void finalize() {
        _statement.release();
      }
    });
  }

  @Override
  public Flow<List<String>> getAllCategories() {
    final String _sql = "SELECT DISTINCT category FROM products";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"products"}, new Callable<List<String>>() {
      @Override
      @NonNull
      public List<String> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final List<String> _result = new ArrayList<String>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final String _item;
            _item = _cursor.getString(0);
            _result.add(_item);
          }
          return _result;
        } finally {
          _cursor.close();
        }
      }

      @Override
      protected void finalize() {
        _statement.release();
      }
    });
  }

  @Override
  public Object count(final Continuation<? super Integer> $completion) {
    final String _sql = "SELECT COUNT(*) FROM products";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<Integer>() {
      @Override
      @NonNull
      public Integer call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final Integer _result;
          if (_cursor.moveToFirst()) {
            final int _tmp;
            _tmp = _cursor.getInt(0);
            _result = _tmp;
          } else {
            _result = 0;
          }
          return _result;
        } finally {
          _cursor.close();
          _statement.release();
        }
      }
    }, $completion);
  }

  @NonNull
  public static List<Class<?>> getRequiredConverters() {
    return Collections.emptyList();
  }
}
