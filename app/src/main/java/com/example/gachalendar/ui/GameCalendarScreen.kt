package com.example.gachalendar.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.gachalendar.model.Game
import com.example.gachalendar.model.GameEvent
import com.example.gachalendar.model.EventType
import java.time.LocalDateTime

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GameCalendarScreen(
    game: Game,
    events: List<GameEvent>,
    onBackClick: () -> Unit,
    onEventClick: (GameEvent) -> Unit,
    onRefresh: () -> Unit
) {
    val gameEvents = events.filter { it.gameId == game.id }
        .sortedBy { it.endTime }

    var isTimelineView by remember { mutableStateOf(false) }
    var selectedTab by remember { mutableStateOf(0) }

    val filteredEvents = remember(gameEvents, selectedTab) {
        gameEvents.filter { event ->
            when (selectedTab) {
                0 -> event.type == EventType.BANNER
                1 -> event.type == EventType.IN_GAME_EVENT || event.type == EventType.LOGIN_EVENT || event.type == EventType.MAINTENANCE || event.type == EventType.OTHER
                2 -> event.type == EventType.ENDGAME
                else -> true
            }
        }
    }

    val gameGradients = mapOf(
        "gi" to listOf(Color(0xFF13223C), Color(0xFF0A1220)),
        "hsr" to listOf(Color(0xFF281440), Color(0xFF140A20)),
        "wuwa" to listOf(Color(0xFF1A1A1A), Color(0xFF0F0F0F)),
        "zzz" to listOf(Color(0xFF072013), Color(0xFF030D08)),
        "endfield" to listOf(Color(0xFF4D2200), Color(0xFF261100)),
        "nte" to listOf(Color(0xFF07333C), Color(0xFF03181C)),
        "p5x" to listOf(Color(0xFF4A0707), Color(0xFF240303))
    )
    val currentGradient = gameGradients[game.id] ?: listOf(Color(0xFF1E1E1E), Color(0xFF121212))

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        currentGradient[0],
                        currentGradient[1],
                        Color(0xFF080C14)
                    )
                )
            )
    ) {
        Scaffold(
            containerColor = Color.Transparent,
            topBar = {
                TopAppBar(
                    title = { Text(game.name, fontWeight = FontWeight.Bold, color = Color.White) },
                    navigationIcon = {
                        IconButton(onClick = onBackClick) {
                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                                contentDescription = "Back",
                                tint = Color.White
                            )
                        }
                    },
                    actions = {
                        IconButton(onClick = onRefresh) {
                            Icon(
                                imageVector = Icons.Default.Refresh,
                                contentDescription = "Refresh",
                                tint = Color.White
                            )
                        }
                    },
                    colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = Color.Transparent,
                        titleContentColor = Color.White
                    )
                )
            },
            floatingActionButton = {
                ExtendedFloatingActionButton(
                    onClick = { isTimelineView = !isTimelineView },
                    containerColor = currentGradient[0],
                    contentColor = Color.White,
                    shape = RoundedCornerShape(24.dp),
                    elevation = FloatingActionButtonDefaults.elevation(defaultElevation = 8.dp)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        modifier = Modifier.padding(horizontal = 4.dp)
                    ) {
                        Icon(
                            imageVector = if (isTimelineView) Icons.Default.List else Icons.Default.DateRange,
                            contentDescription = null,
                            tint = Color.White
                        )
                        Text(if (isTimelineView) "List View" else "Timeline View", fontWeight = FontWeight.Bold)
                    }
                }
            }
        ) { paddingValues ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
            ) {
                // Custom Capsule Tab Bar
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 8.dp)
                        .background(Color(0x11FFFFFF), RoundedCornerShape(24.dp))
                        .padding(4.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    val tabTitles = listOf("Banner Rate Up", "Event Terbatas", "Konten Endgame")
                    tabTitles.forEachIndexed { index, title ->
                        val isSelected = selectedTab == index
                        Box(
                            modifier = Modifier
                                .weight(1f)
                                .height(38.dp)
                                .background(
                                    if (isSelected) currentGradient[0] else Color.Transparent,
                                    RoundedCornerShape(20.dp)
                                )
                                .clickable { selectedTab = index },
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = title,
                                color = if (isSelected) Color.White else Color.White.copy(alpha = 0.6f),
                                fontWeight = FontWeight.Bold,
                                fontSize = 12.sp
                            )
                        }
                    }
                }

                Box(modifier = Modifier.weight(1f)) {
                    if (isTimelineView) {
                        TimelineView(
                            events = filteredEvents,
                            onEventClick = onEventClick,
                            modifier = Modifier.fillMaxSize()
                        )
                    } else {
                        LazyColumn(
                            modifier = Modifier
                                .fillMaxSize()
                                .padding(horizontal = 16.dp),
                            verticalArrangement = Arrangement.spacedBy(12.dp),
                            contentPadding = PaddingValues(bottom = 80.dp, top = 8.dp)
                        ) {
                            if (filteredEvents.isEmpty()) {
                                item {
                                    Box(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(top = 40.dp),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        Text(
                                            "Tidak ada event aktif di kategori ini.",
                                            color = Color.White.copy(alpha = 0.6f),
                                            fontWeight = FontWeight.Medium,
                                            fontSize = 14.sp
                                        )
                                    }
                                }
                            } else {
                                items(filteredEvents) { event ->
                                    EventCard(
                                        event = event,
                                        onClick = { onEventClick(event) }
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
