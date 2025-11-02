// FiscalAI v5.0 - Frontend JavaScript

// Estado da aplicação
const app = {
    arquivosCarregados: {
        cabecalho: false,
        itens: false,
        cfop: false
    },
    agenteAtivo: false
};

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    setupEnterKey();
    checkHealth();
});

// Setup das abas
function setupTabs() {
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remover active de todas as tabs
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(tc => tc.style.display = 'none');
            
            // Ativar tab clicada
            tab.classList.add('active');
            const tabName = tab.dataset.tab;
            const content = document.getElementById(`tab-${tabName}`);
            if (content) {
                content.style.display = 'block';
                
                // Carregar estatísticas se for a aba de estatísticas
                if (tabName === 'estatisticas') {
                    carregarEstatisticas();
                }
            }
        });
    });
}

// Setup para enviar mensagem com Enter
function setupEnterKey() {
    const input = document.getElementById('chat-input');
    if (input) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                enviarMensagem();
            }
        });
    }
}

async function checkHealth() {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        // Corrigido: usar agente_inicializado (compatível com v4)
        app.agenteAtivo = data.agente_inicializado || data.agente_ativo;
        app.arquivosCarregados = data.arquivos_carregados;
        
        updateUI();
    } catch (error) {
        console.error('Erro ao verificar saúde:', error);
    }
}

// Atualizar UI baseado no estado
function updateUI() {
    // Atualizar botão de inicializar
    const btnInicializar = document.getElementById('btn-inicializar');
    if (btnInicializar) {
        const todosCarregados = Object.values(app.arquivosCarregados).every(v => v);
        btnInicializar.disabled = !todosCarregados || app.agenteAtivo;
        
        if (app.agenteAtivo) {
            btnInicializar.textContent = '✅ Sistema Inicializado';
            btnInicializar.style.background = '#10b981';
        }
    }
    
    // Habilitar/desabilitar controles do chat
    const chatInput = document.getElementById('chat-input');
    const btnEnviar = document.getElementById('btn-enviar');
    
    if (chatInput) chatInput.disabled = !app.agenteAtivo;
    if (btnEnviar) btnEnviar.disabled = !app.agenteAtivo;
    
    // Habilitar/desabilitar quick actions
    const quickActions = document.querySelectorAll('.quick-actions button:not(:last-child)');
    quickActions.forEach(btn => {
        btn.disabled = !app.agenteAtivo;
    });
}

// Upload de arquivo
async function uploadFile(tipo) {
    const fileInput = document.getElementById(`file-${tipo}`);
    const statusSpan = document.getElementById(`status-${tipo}`);
    
    if (!fileInput.files[0]) {
        alert('Por favor, selecione um arquivo');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    statusSpan.textContent = '⏳ Enviando...';
    statusSpan.className = 'status';
    
    try {
        const response = await fetch(`/api/upload/${tipo}`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            statusSpan.textContent = `✅ ${data.message}`;
            statusSpan.className = 'status success';
            app.arquivosCarregados[tipo] = true;
            updateUI();
        } else {
            throw new Error(data.error || 'Erro ao enviar arquivo');
        }
    } catch (error) {
        statusSpan.textContent = `❌ ${error.message}`;
        statusSpan.className = 'status error';
    }
}

// Inicializar agente
async function inicializarAgente() {
    const btn = document.getElementById('btn-inicializar');
    const originalText = btn.textContent;
    
    btn.textContent = '⏳ Inicializando...';
    btn.disabled = true;
    
    try {
        const response = await fetch('/api/inicializar', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            app.agenteAtivo = true;
            alert('✅ Sistema inicializado com sucesso! Você pode ir para a aba Chat IA.');
            updateUI();
            
            // Mudar para aba chat
            document.querySelector('[data-tab="chat"]').click();
        } else {
            throw new Error(data.error || 'Erro ao inicializar');
        }
    } catch (error) {
        alert(`❌ Erro: ${error.message}`);
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

// Enviar mensagem no chat
async function enviarMensagem() {
    const input = document.getElementById('chat-input');
    const mensagem = input.value.trim();
    
    if (!mensagem) return;
    
    // Adicionar mensagem do usuário
    adicionarMensagem(mensagem, 'user');
    input.value = '';
    
    // Mostrar loading
    const loadingDiv = adicionarMensagem('Pensando... <span class="loading"></span>', 'assistant');
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ mensagem })
        });
        
        const data = await response.json();
        
        // Remover loading
        loadingDiv.remove();
        
        if (data.success) {
            adicionarMensagem(data.resposta, 'assistant');
        } else {
            throw new Error(data.error || 'Erro ao processar mensagem');
        }
    } catch (error) {
        loadingDiv.remove();
        adicionarMensagem(`❌ Erro: ${error.message}`, 'system');
    }
}

// Adicionar mensagem ao chat
function adicionarMensagem(texto, tipo) {
    const messagesDiv = document.getElementById('chat-messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${tipo}`;
    messageDiv.innerHTML = `<div class="message-content">${texto}</div>`;
    
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    return messageDiv;
}

// Quick actions
async function totalNotas() {
    const input = document.getElementById('chat-input');
    input.value = 'Quantas notas fiscais temos no sistema?';
    enviarMensagem();
}

async function cfopsPopulares() {
    adicionarMensagem('Quais são os CFOPs mais utilizados?', 'user');
    
    const loadingDiv = adicionarMensagem('Carregando... <span class="loading"></span>', 'assistant');
    
    try {
        const response = await fetch('/api/cfops_populares');
        const data = await response.json();
        
        loadingDiv.remove();
        
        if (data.success) {
            let resposta = '📊 CFOPs Mais Utilizados:\n\n';
            data.data.forEach((cfop, index) => {
                resposta += `${index + 1}. CFOP ${cfop.codigo} - ${cfop.count} ocorrências\n`;
            });
            adicionarMensagem(resposta, 'assistant');
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        loadingDiv.remove();
        adicionarMensagem(`❌ Erro: ${error.message}`, 'system');
    }
}

function explicarCFOP() {
    const cfop = prompt('Digite o CFOP que deseja explicar (ex: 5102):');
    if (cfop) {
        const input = document.getElementById('chat-input');
        input.value = `Explique o CFOP ${cfop}`;
        enviarMensagem();
    }
}

function limparChat() {
    const messagesDiv = document.getElementById('chat-messages');
    messagesDiv.innerHTML = '';
}

// Carregar estatísticas
async function carregarEstatisticas() {
    const statsContent = document.getElementById('stats-content');
    
    if (!app.agenteAtivo) {
        statsContent.innerHTML = '<p class="warning">⚠️ Faça upload dos arquivos primeiro</p>';
        return;
    }
    
    statsContent.innerHTML = '<p>⏳ Carregando estatísticas...</p>';
    
    try {
        const response = await fetch('/api/estatisticas');
        const data = await response.json();
        
        if (data.success) {
            const stats = data.data;
            statsContent.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>📋 Total de Notas</h3>
                        <p class="stat-value">${stats.total_notas || 0}</p>
                    </div>
                    <div class="stat-card">
                        <h3>📦 Total de Itens</h3>
                        <p class="stat-value">${stats.total_itens || 0}</p>
                    </div>
                    <div class="stat-card">
                        <h3>🏷️ CFOPs Únicos</h3>
                        <p class="stat-value">${stats.cfops_unicos || 0}</p>
                    </div>
                </div>
            `;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        statsContent.innerHTML = `<p class="warning">❌ Erro ao carregar estatísticas: ${error.message}</p>`;
    }
}

// Validar CFOP
async function validarCFOP() {
    const chaveNF = document.getElementById('chave-nf').value.trim();
    const numeroItem = document.getElementById('numero-item').value.trim();
    const resultDiv = document.getElementById('validation-result');
    
    if (!chaveNF || !numeroItem) {
        alert('Por favor, preencha todos os campos');
        return;
    }
    
    resultDiv.innerHTML = '<p>⏳ Validando...</p>';
    resultDiv.classList.add('show');
    
    try {
        const response = await fetch('/api/validar_cfop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                chave_nf: chaveNF,
                numero_item: parseInt(numeroItem)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const resultado = data.resultado;
            resultDiv.innerHTML = `
                <h3>Resultado da Validação</h3>
                <pre>${JSON.stringify(resultado, null, 2)}</pre>
            `;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        resultDiv.innerHTML = `<p class="warning">❌ Erro: ${error.message}</p>`;
    }
}
