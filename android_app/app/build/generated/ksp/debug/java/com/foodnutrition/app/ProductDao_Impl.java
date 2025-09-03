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
        return "INSERT OR REPLACE INTO `products` (`id`,`productName`,`brand`,`category`,`ingredients`,`servingSize`,`nutritionPer`,`energyKcal100g`,`fat100g`,`saturatedFat100g`,`carbs100g`,`sugars100g`,`protein100g`,`salt100g`,`fiber100g`,`sodium100g`) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final Product entity) {
        statement.bindString(1, entity.getId());
        if (entity.getProductName() == null) {
          statement.bindNull(2);
        } else {
          statement.bindString(2, entity.getProductName());
        }
        if (entity.getBrand() == null) {
          statement.bindNull(3);
        } else {
          statement.bindString(3, entity.getBrand());
        }
        if (entity.getCategory() == null) {
          statement.bindNull(4);
        } else {
          statement.bindString(4, entity.getCategory());
        }
        if (entity.getIngredients() == null) {
          statement.bindNull(5);
        } else {
          statement.bindString(5, entity.getIngredients());
        }
        if (entity.getServingSize() == null) {
          statement.bindNull(6);
        } else {
          statement.bindString(6, entity.getServingSize());
        }
        if (entity.getNutritionPer() == null) {
          statement.bindNull(7);
        } else {
          statement.bindString(7, entity.getNutritionPer());
        }
        if (entity.getEnergyKcal100g() == null) {
          statement.bindNull(8);
        } else {
          statement.bindDouble(8, entity.getEnergyKcal100g());
        }
        if (entity.getFat100g() == null) {
          statement.bindNull(9);
        } else {
          statement.bindDouble(9, entity.getFat100g());
        }
        if (entity.getSaturatedFat100g() == null) {
          statement.bindNull(10);
        } else {
          statement.bindDouble(10, entity.getSaturatedFat100g());
        }
        if (entity.getCarbs100g() == null) {
          statement.bindNull(11);
        } else {
          statement.bindDouble(11, entity.getCarbs100g());
        }
        if (entity.getSugars100g() == null) {
          statement.bindNull(12);
        } else {
          statement.bindDouble(12, entity.getSugars100g());
        }
        if (entity.getProtein100g() == null) {
          statement.bindNull(13);
        } else {
          statement.bindDouble(13, entity.getProtein100g());
        }
        if (entity.getSalt100g() == null) {
          statement.bindNull(14);
        } else {
          statement.bindDouble(14, entity.getSalt100g());
        }
        if (entity.getFiber100g() == null) {
          statement.bindNull(15);
        } else {
          statement.bindDouble(15, entity.getFiber100g());
        }
        if (entity.getSodium100g() == null) {
          statement.bindNull(16);
        } else {
          statement.bindDouble(16, entity.getSodium100g());
        }
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
          final int _cursorIndexOfProductName = CursorUtil.getColumnIndexOrThrow(_cursor, "productName");
          final int _cursorIndexOfBrand = CursorUtil.getColumnIndexOrThrow(_cursor, "brand");
          final int _cursorIndexOfCategory = CursorUtil.getColumnIndexOrThrow(_cursor, "category");
          final int _cursorIndexOfIngredients = CursorUtil.getColumnIndexOrThrow(_cursor, "ingredients");
          final int _cursorIndexOfServingSize = CursorUtil.getColumnIndexOrThrow(_cursor, "servingSize");
          final int _cursorIndexOfNutritionPer = CursorUtil.getColumnIndexOrThrow(_cursor, "nutritionPer");
          final int _cursorIndexOfEnergyKcal100g = CursorUtil.getColumnIndexOrThrow(_cursor, "energyKcal100g");
          final int _cursorIndexOfFat100g = CursorUtil.getColumnIndexOrThrow(_cursor, "fat100g");
          final int _cursorIndexOfSaturatedFat100g = CursorUtil.getColumnIndexOrThrow(_cursor, "saturatedFat100g");
          final int _cursorIndexOfCarbs100g = CursorUtil.getColumnIndexOrThrow(_cursor, "carbs100g");
          final int _cursorIndexOfSugars100g = CursorUtil.getColumnIndexOrThrow(_cursor, "sugars100g");
          final int _cursorIndexOfProtein100g = CursorUtil.getColumnIndexOrThrow(_cursor, "protein100g");
          final int _cursorIndexOfSalt100g = CursorUtil.getColumnIndexOrThrow(_cursor, "salt100g");
          final int _cursorIndexOfFiber100g = CursorUtil.getColumnIndexOrThrow(_cursor, "fiber100g");
          final int _cursorIndexOfSodium100g = CursorUtil.getColumnIndexOrThrow(_cursor, "sodium100g");
          final List<Product> _result = new ArrayList<Product>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final Product _item;
            final String _tmpId;
            _tmpId = _cursor.getString(_cursorIndexOfId);
            final String _tmpProductName;
            if (_cursor.isNull(_cursorIndexOfProductName)) {
              _tmpProductName = null;
            } else {
              _tmpProductName = _cursor.getString(_cursorIndexOfProductName);
            }
            final String _tmpBrand;
            if (_cursor.isNull(_cursorIndexOfBrand)) {
              _tmpBrand = null;
            } else {
              _tmpBrand = _cursor.getString(_cursorIndexOfBrand);
            }
            final String _tmpCategory;
            if (_cursor.isNull(_cursorIndexOfCategory)) {
              _tmpCategory = null;
            } else {
              _tmpCategory = _cursor.getString(_cursorIndexOfCategory);
            }
            final String _tmpIngredients;
            if (_cursor.isNull(_cursorIndexOfIngredients)) {
              _tmpIngredients = null;
            } else {
              _tmpIngredients = _cursor.getString(_cursorIndexOfIngredients);
            }
            final String _tmpServingSize;
            if (_cursor.isNull(_cursorIndexOfServingSize)) {
              _tmpServingSize = null;
            } else {
              _tmpServingSize = _cursor.getString(_cursorIndexOfServingSize);
            }
            final String _tmpNutritionPer;
            if (_cursor.isNull(_cursorIndexOfNutritionPer)) {
              _tmpNutritionPer = null;
            } else {
              _tmpNutritionPer = _cursor.getString(_cursorIndexOfNutritionPer);
            }
            final Double _tmpEnergyKcal100g;
            if (_cursor.isNull(_cursorIndexOfEnergyKcal100g)) {
              _tmpEnergyKcal100g = null;
            } else {
              _tmpEnergyKcal100g = _cursor.getDouble(_cursorIndexOfEnergyKcal100g);
            }
            final Double _tmpFat100g;
            if (_cursor.isNull(_cursorIndexOfFat100g)) {
              _tmpFat100g = null;
            } else {
              _tmpFat100g = _cursor.getDouble(_cursorIndexOfFat100g);
            }
            final Double _tmpSaturatedFat100g;
            if (_cursor.isNull(_cursorIndexOfSaturatedFat100g)) {
              _tmpSaturatedFat100g = null;
            } else {
              _tmpSaturatedFat100g = _cursor.getDouble(_cursorIndexOfSaturatedFat100g);
            }
            final Double _tmpCarbs100g;
            if (_cursor.isNull(_cursorIndexOfCarbs100g)) {
              _tmpCarbs100g = null;
            } else {
              _tmpCarbs100g = _cursor.getDouble(_cursorIndexOfCarbs100g);
            }
            final Double _tmpSugars100g;
            if (_cursor.isNull(_cursorIndexOfSugars100g)) {
              _tmpSugars100g = null;
            } else {
              _tmpSugars100g = _cursor.getDouble(_cursorIndexOfSugars100g);
            }
            final Double _tmpProtein100g;
            if (_cursor.isNull(_cursorIndexOfProtein100g)) {
              _tmpProtein100g = null;
            } else {
              _tmpProtein100g = _cursor.getDouble(_cursorIndexOfProtein100g);
            }
            final Double _tmpSalt100g;
            if (_cursor.isNull(_cursorIndexOfSalt100g)) {
              _tmpSalt100g = null;
            } else {
              _tmpSalt100g = _cursor.getDouble(_cursorIndexOfSalt100g);
            }
            final Double _tmpFiber100g;
            if (_cursor.isNull(_cursorIndexOfFiber100g)) {
              _tmpFiber100g = null;
            } else {
              _tmpFiber100g = _cursor.getDouble(_cursorIndexOfFiber100g);
            }
            final Double _tmpSodium100g;
            if (_cursor.isNull(_cursorIndexOfSodium100g)) {
              _tmpSodium100g = null;
            } else {
              _tmpSodium100g = _cursor.getDouble(_cursorIndexOfSodium100g);
            }
            _item = new Product(_tmpId,_tmpProductName,_tmpBrand,_tmpCategory,_tmpIngredients,_tmpServingSize,_tmpNutritionPer,_tmpEnergyKcal100g,_tmpFat100g,_tmpSaturatedFat100g,_tmpCarbs100g,_tmpSugars100g,_tmpProtein100g,_tmpSalt100g,_tmpFiber100g,_tmpSodium100g);
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
