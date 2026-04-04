package com.bbf.gigshield.network

import com.google.gson.JsonParser

fun parseApiErrorMessage(body: String?): String {
    if (body.isNullOrBlank()) return "Request failed"
    return try {
        val o = JsonParser.parseString(body).asJsonObject
        val d = o.get("detail") ?: return body
        when {
            d.isJsonPrimitive -> d.asString
            d.isJsonArray -> d.asJsonArray.firstOrNull()?.asJsonObject?.get("msg")?.asString ?: body
            else -> body
        }
    } catch (_: Exception) {
        body
    }
}
