package com.example.gachalendar.ui

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import kotlinx.coroutines.delay
import java.time.LocalDate

@Composable
fun SplashScreen(
    onAnimationFinished: () -> Unit
) {
    var startEntrance by remember { mutableStateOf(false) }
    
    // Trigger entrance animation on start
    LaunchedEffect(Unit) {
        startEntrance = true
        // Keep splash active for 2.6 seconds, then transition
        delay(2600)
        onAnimationFinished()
    }

    val scale by animateFloatAsState(
        targetValue = if (startEntrance) 1f else 0.4f,
        animationSpec = spring(
            dampingRatio = Spring.DampingRatioMediumBouncy,
            stiffness = Spring.StiffnessLow
        ),
        label = "logo_scale"
    )

    val alpha by animateFloatAsState(
        targetValue = if (startEntrance) 1f else 0f,
        animationSpec = tween(1000, easing = EaseInOutQuad),
        label = "logo_alpha"
    )

    val textOffset by animateDpAsState(
        targetValue = if (startEntrance) 0.dp else 40.dp,
        animationSpec = spring(
            dampingRatio = Spring.DampingRatioNoBouncy,
            stiffness = Spring.StiffnessMedium
        ),
        label = "text_offset"
    )

    val infiniteTransition = rememberInfiniteTransition(label = "cyber_glow")
    
    // Rotating cyber rings
    val ringRotation by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(8000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "ring_rotation"
    )

    // Pulsing cyber glow scale
    val glowScale by infiniteTransition.animateFloat(
        initialValue = 1.0f,
        targetValue = 1.25f,
        animationSpec = infiniteRepeatable(
            animation = tween(1500, easing = EaseInOutSine),
            repeatMode = RepeatMode.Reverse
        ),
        label = "glow_scale"
    )

    // Pulsing cyber glow alpha
    val glowAlpha by infiniteTransition.animateFloat(
        initialValue = 0.15f,
        targetValue = 0.45f,
        animationSpec = infiniteRepeatable(
            animation = tween(1500, easing = EaseInOutSine),
            repeatMode = RepeatMode.Reverse
        ),
        label = "glow_alpha"
    )

    // Loading progress bar (0.0 to 1.0)
    val progress by animateFloatAsState(
        targetValue = if (startEntrance) 1f else 0f,
        animationSpec = tween(2200, easing = EaseOutQuad),
        label = "progress"
    )

    // Dynamic futuristic console logging text based on progress
    val consoleText = when {
        progress < 0.3f -> "INITIALIZING SYSTEM..."
        progress < 0.6f -> "CONNECTING TO EVENTS PROTOCOLS..."
        progress < 0.85f -> "SYNCING GACHALENDAR DATABASES..."
        else -> "INTERFACE STABILIZED. GACHALENDAR ONLINE!"
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        Color(0xFF070B19), // Deep Space Dark Slate 950
                        Color(0xFF0F172A)  // Slate 900
                    )
                )
            ),
        contentAlignment = Alignment.Center
    ) {
        // Futuristic background decoration (Dotted circle Grid)
        Box(
            modifier = Modifier
                .size(360.dp)
                .graphicsLayer {
                    this.scaleX = glowScale * 0.9f
                    this.scaleY = glowScale * 0.9f
                }
                .alpha(glowAlpha * 0.5f)
                .border(2.dp, Brush.radialGradient(colors = listOf(Color(0xFF3F51B5), Color.Transparent)), CircleShape)
        )

        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
            modifier = Modifier.fillMaxWidth()
        ) {
            // Logo Container with pulsing glow & rotating cyber borders
            Box(
                contentAlignment = Alignment.Center,
                modifier = Modifier
                    .size(160.dp)
                    .scale(scale)
                    .alpha(alpha)
            ) {
                // Cyber Glow Ring 1 (Pulse)
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .graphicsLayer {
                            scaleX = glowScale
                            scaleY = glowScale
                        }
                        .alpha(glowAlpha)
                        .background(
                            Brush.radialGradient(
                                colors = listOf(
                                    Color(0xFF3F51B5).copy(alpha = 0.6f),
                                    Color.Transparent
                                )
                            ),
                            CircleShape
                        )
                )

                // Cyber Dotted Ring 2 (Rotate)
                Box(
                    modifier = Modifier
                        .size(136.dp)
                        .rotate(ringRotation)
                        .border(
                            2.dp,
                            Brush.sweepGradient(
                                colors = listOf(
                                    Color(0xFF3F51B5),
                                    Color(0xFFE91E63),
                                    Color.Transparent,
                                    Color(0xFF3F51B5)
                                )
                            ),
                            CircleShape
                        )
                )

                // Main circular logo (loaded from resources)
                AsyncImage(
                    model = "android.resource://com.example.gachalendar/drawable/ic_logo",
                    contentDescription = "Gachalendar Logo",
                    contentScale = ContentScale.Crop,
                    modifier = Modifier
                        .size(100.dp)
                        .clip(CircleShape)
                        .border(2.dp, Color.White.copy(alpha = 0.2f), CircleShape)
                )
            }

            Spacer(modifier = Modifier.height(24.dp))

            // App Title & Tagline
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier
                    .offset(y = textOffset)
                    .alpha(alpha)
            ) {
                Text(
                    text = "Gachalendar",
                    fontSize = 32.sp,
                    fontWeight = FontWeight.Black,
                    color = Color.White
                )
                
                Spacer(modifier = Modifier.height(6.dp))
                
                Text(
                    text = "NEXT-GEN TIMELINE MONITOR",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFFE91E63) // Cyber Pink Accent
                )
            }

            Spacer(modifier = Modifier.height(80.dp))

            // Cyber Progress Area (Fixed at bottom)
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier
                    .width(260.dp)
                    .alpha(alpha)
            ) {
                // Console Log Text
                Text(
                    text = consoleText,
                    fontSize = 10.sp,
                    fontFamily = FontFamily.Monospace,
                    fontWeight = FontWeight.Bold,
                    color = Color.White.copy(alpha = 0.6f),
                    maxLines = 1
                )
                
                Spacer(modifier = Modifier.height(10.dp))

                // Progress Bar Container
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(4.dp)
                        .background(Color.White.copy(alpha = 0.08f), RoundedCornerShape(2.dp))
                ) {
                    // Glowing progress indicator
                    Box(
                        modifier = Modifier
                            .fillMaxHeight()
                            .fillMaxWidth(progress)
                            .background(
                                Brush.horizontalGradient(
                                    colors = listOf(
                                        Color(0xFF3F51B5), // Indigo
                                        Color(0xFFE91E63)  // Pink
                                    )
                                ),
                                RoundedCornerShape(2.dp)
                            )
                            .border(
                                width = 1.dp,
                                color = Color.White.copy(alpha = 0.4f),
                                shape = RoundedCornerShape(2.dp)
                            )
                    )
                }
                
                Spacer(modifier = Modifier.height(8.dp))
                
                // Percentage Text
                Text(
                    text = "${(progress * 100).toInt()}%",
                    fontSize = 11.sp,
                    fontFamily = FontFamily.Monospace,
                    fontWeight = FontWeight.Black,
                    color = Color.White.copy(alpha = 0.8f)
                )
            }
        }
    }
}
