package com.bbf.gigshield.data

import android.content.Context

object TokenStore {
    private const val PREFS = "gigshield_auth"
    private const val KEY_TOKEN = "access_token"

    fun saveAccessToken(context: Context, token: String) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit()
            .putString(KEY_TOKEN, token)
            .apply()
    }

    fun getAccessToken(context: Context): String? =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getString(KEY_TOKEN, null)
}
