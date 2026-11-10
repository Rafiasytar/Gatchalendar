package com.example.gachalendar.ui

import androidx.compose.material.icons.Icons
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.vector.path
import androidx.compose.ui.unit.dp

val Icons.History: ImageVector
    get() {
        if (_history != null) {
            return _history!!
        }
        _history = ImageVector.Builder(
            name = "History",
            defaultWidth = 24.dp,
            defaultHeight = 24.dp,
            viewportWidth = 24f,
            viewportHeight = 24f
        ).path(fill = SolidColor(Color.White)) {
            moveTo(13.0f, 3.0f)
            curveTo(8.03f, 3.0f, 4.0f, 7.03f, 4.0f, 12.0f)
            horizontalLineTo(1.0f)
            lineToRelative(4.0f, 4.0f)
            lineToRelative(4.0f, -4.0f)
            horizontalLineTo(6.0f)
            curveTo(6.0f, 8.13f, 9.13f, 5.0f, 13.0f, 5.0f)
            curveToRelative(3.87f, 0.0f, 7.0f, 3.13f, 7.0f, 7.0f)
            curveToRelative(0.0f, 3.87f, -3.13f, 7.0f, -7.0f, 7.0f)
            curveToRelative(-1.93f, 0.0f, -3.68f, -0.79f, -4.94f, -2.06f)
            lineToRelative(-1.42f, 1.42f)
            curveTo(8.27f, 19.99f, 10.51f, 21.0f, 13.0f, 21.0f)
            curveToRelative(4.97f, 0.0f, 9.0f, -4.03f, 9.0f, -9.0f)
            curveToRelative(0.0f, -4.97f, -4.03f, -9.0f, -9.0f, -9.0f)
            close()
            moveTo(12.0f, 8.0f)
            verticalLineToRelative(5.0f)
            lineToRelative(4.25f, 2.52f)
            lineToRelative(0.75f, -1.23f)
            lineToRelative(-3.5f, -2.08f)
            verticalLineTo(8.0f)
            horizontalLineTo(12.0f)
            close()
        }.build()
        return _history!!
    }

private var _history: ImageVector? = null
