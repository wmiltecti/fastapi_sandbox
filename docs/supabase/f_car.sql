USE [ambiental_hom]
GO

/****** Object:  Table [dbo].[f_CAR]    Script Date: 27/10/2025 09:57:17 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[f_CAR](
	[id] [int] NOT NULL,
	[passoAtual] [int] NOT NULL,
	[possuiAtividadeAnteriorMarco] [tinyint] NULL,
	[aderirPrograma] [tinyint] NULL,
	[arquivoGeorreferenciamento] [varchar](250) NULL,
	[possuiTituloCotaReservaLegal] [tinyint] NULL,
	[possuiMultasEmAberto] [tinyint] NULL,
	[existeTermoAjusteConduta] [tinyint] NULL,
	[sobrePosicaoAreaTotal] [tinyint] NULL,
	[sobrePosicaoReservaLegal] [tinyint] NULL,
	[reciboCarNacional] [varchar](255) NULL,
	[situacaoCar_id] [int] NOT NULL,
	[aceitoTermoAdesaoPRA] [tinyint] NULL,
	[codigoSeguranca] [varchar](100) NULL,
	[imovel_id] [int] NOT NULL,
	[pessoaCadastrante_id] [int] NOT NULL,
	[projecaoGeorreferenciamento_id] [int] NULL,
	[sobreposicaoAreaImovel_id] [int] NULL,
	[termoAjusteConduta_id] [int] NULL,
	[metodoRecuperacaoAreaRestauracao_id] [int] NULL,
	[situacaoPagamento_id] [int] NULL,
	[regularizacaoPassivoApp_id] [int] NULL,
	[regularizacaoPassivoRL_id] [int] NULL,
	[configuracaoCobrancaCAR_id] [int] NULL,
	[centroide] [varchar](1024) NULL,
	[dataAprovacao] [datetime] NULL,
	[responsavelAprovacao_id] [int] NULL,
	[areaTotalApp] [float] NULL,
	[dataRetornoSicar] [datetime] NULL,
	[prazoVigenciaTCRAE] [int] NULL,
	[temporariedadeTCRAE_id] [int] NULL,
	[regimeDeUso_id] [int] NULL,
	[numeroTituloCotas] [tinyint] NULL,
	[codSegurancaTitulo] [varchar](30) NULL,
	[possuiRLEmOutroImovelCondominio] [tinyint] NULL,
	[dataHoraSuspensao] [datetime] NULL,
	[bloqueadoEdicao] [tinyint] NULL,
	[origemBloqueio] [varchar](80) NULL,
	[tecnicoBloqueioEdicao_id] [int] NULL,
	[dataBloqueioEdicao] [datetime] NULL,
	[regimeUsoArea] [float] NULL,
	[mostrarSaldoCotasCRAE] [tinyint] NULL,
	[condicaoAnaliseSicar_id] [int] NULL,
	[solicitacaoDeCancelamentoDeferida] [tinyint] NOT NULL,
	[retificacaoDocumental] [tinyint] NOT NULL,
	[hashblockchain] [varchar](100) NULL,
	[arquivoShapeBytes] [varbinary](max) NULL,
	[dataArquivoShape] [datetime] NULL,
	[dataProcessamentoArquivoShape] [datetime] NULL,
 CONSTRAINT [pk_CAR] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 90, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

ALTER TABLE [dbo].[f_CAR] ADD  DEFAULT ((0)) FOR [bloqueadoEdicao]
GO

ALTER TABLE [dbo].[f_CAR] ADD  DEFAULT ((0)) FOR [regimeUsoArea]
GO

ALTER TABLE [dbo].[f_CAR] ADD  DEFAULT ((0)) FOR [solicitacaoDeCancelamentoDeferida]
GO

ALTER TABLE [dbo].[f_CAR] ADD  DEFAULT ((0)) FOR [retificacaoDocumental]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fCARpssoaCadastranteid] FOREIGN KEY([pessoaCadastrante_id])
REFERENCES [dbo].[f_pessoa] ([pkpessoa])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fCARpssoaCadastranteid]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fCRcnfgrcCobrancaCARid] FOREIGN KEY([configuracaoCobrancaCAR_id])
REFERENCES [dbo].[f_ConfiguracaoCobrancaCAR] ([id])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fCRcnfgrcCobrancaCARid]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fCRprjcGrrfrncamentoid] FOREIGN KEY([projecaoGeorreferenciamento_id])
REFERENCES [dbo].[f_projecao] ([pkprojecao])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fCRprjcGrrfrncamentoid]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fCRrglrzcaoPassivoRLid] FOREIGN KEY([regularizacaoPassivoRL_id])
REFERENCES [dbo].[f_RegularizacaoPassivoRL] ([id])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fCRrglrzcaoPassivoRLid]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fCRrglrzcoPassivoAppid] FOREIGN KEY([regularizacaoPassivoApp_id])
REFERENCES [dbo].[f_RegularizacaoPassivoApp] ([id])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fCRrglrzcoPassivoAppid]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fCRrspnsvelAprovacaoid] FOREIGN KEY([responsavelAprovacao_id])
REFERENCES [dbo].[f_pessoa] ([pkpessoa])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fCRrspnsvelAprovacaoid]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fCRsbrpscoAreaImovelid] FOREIGN KEY([sobreposicaoAreaImovel_id])
REFERENCES [dbo].[f_SobreposicaoAreaImovel] ([id])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fCRsbrpscoAreaImovelid]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fCRtcncBlqueioEdicaoid] FOREIGN KEY([tecnicoBloqueioEdicao_id])
REFERENCES [dbo].[f_pessoa] ([pkpessoa])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fCRtcncBlqueioEdicaoid]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fCRtrmoAjusteCondutaid] FOREIGN KEY([termoAjusteConduta_id])
REFERENCES [dbo].[f_TermoAjusteConduta] ([id])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fCRtrmoAjusteCondutaid]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fk_CAR_CondicaoAnaliseSicar] FOREIGN KEY([condicaoAnaliseSicar_id])
REFERENCES [dbo].[f_CondicaoAnaliseSicar] ([id])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fk_CAR_CondicaoAnaliseSicar]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [FK_f_CAR_ID] FOREIGN KEY([id])
REFERENCES [dbo].[f_ProcessoAdministrativo] ([id])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [FK_f_CAR_ID]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [FK_f_CAR_imovel_id] FOREIGN KEY([imovel_id])
REFERENCES [dbo].[f_imovel] ([pkimovel])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [FK_f_CAR_imovel_id]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fk1_CAR_ProcessoAdministrativo] FOREIGN KEY([id])
REFERENCES [dbo].[f_ProcessoAdministrativo] ([id])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fk1_CAR_ProcessoAdministrativo]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fk10_CAR_RegimeDeUso] FOREIGN KEY([regimeDeUso_id])
REFERENCES [dbo].[f_RegimeDeUso] ([id])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fk10_CAR_RegimeDeUso]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fk14_CAR_temporariedadeTCRAE] FOREIGN KEY([temporariedadeTCRAE_id])
REFERENCES [dbo].[f_TipoTemporariedadeTCRAE] ([id])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fk14_CAR_temporariedadeTCRAE]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fk15_tecnicoBloqueioEdicao] FOREIGN KEY([tecnicoBloqueioEdicao_id])
REFERENCES [dbo].[f_pessoa] ([pkpessoa])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fk15_tecnicoBloqueioEdicao]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fk2_CAR_Imovel] FOREIGN KEY([imovel_id])
REFERENCES [dbo].[f_imovel] ([pkimovel])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fk2_CAR_Imovel]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fk3_CAR_SituacaoCar] FOREIGN KEY([situacaoCar_id])
REFERENCES [dbo].[f_SituacaoCar] ([id])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fk3_CAR_SituacaoCar]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fk4_CAR_Pessoa] FOREIGN KEY([pessoaCadastrante_id])
REFERENCES [dbo].[f_pessoa] ([pkpessoa])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fk4_CAR_Pessoa]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fk5_CAR_Projecao] FOREIGN KEY([projecaoGeorreferenciamento_id])
REFERENCES [dbo].[f_projecao] ([pkprojecao])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fk5_CAR_Projecao]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fk6_CAR_RegularizacaoPassivoApp] FOREIGN KEY([regularizacaoPassivoApp_id])
REFERENCES [dbo].[f_RegularizacaoPassivoApp] ([id])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fk6_CAR_RegularizacaoPassivoApp]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fk6_CAR_SobreposicaoAreaImovel] FOREIGN KEY([sobreposicaoAreaImovel_id])
REFERENCES [dbo].[f_SobreposicaoAreaImovel] ([id])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fk6_CAR_SobreposicaoAreaImovel]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fk7_CAR_RegularizacaoPassivoRL] FOREIGN KEY([regularizacaoPassivoRL_id])
REFERENCES [dbo].[f_RegularizacaoPassivoRL] ([id])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fk7_CAR_RegularizacaoPassivoRL]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fk7_CAR_TermoAjusteConduta] FOREIGN KEY([termoAjusteConduta_id])
REFERENCES [dbo].[f_TermoAjusteConduta] ([id])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fk7_CAR_TermoAjusteConduta]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fk8_CAR_MetodoRecuperacaoAreaRestauracao] FOREIGN KEY([metodoRecuperacaoAreaRestauracao_id])
REFERENCES [dbo].[f_MetodoRecuperacaoAreaRestauracao] ([id])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fk8_CAR_MetodoRecuperacaoAreaRestauracao]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fk9_CAR_ConfiguracaoCobrancaCAR] FOREIGN KEY([configuracaoCobrancaCAR_id])
REFERENCES [dbo].[f_ConfiguracaoCobrancaCAR] ([id])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fk9_CAR_ConfiguracaoCobrancaCAR]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fk9_CAR_Pessoa] FOREIGN KEY([responsavelAprovacao_id])
REFERENCES [dbo].[f_pessoa] ([pkpessoa])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fk9_CAR_Pessoa]
GO

ALTER TABLE [dbo].[f_CAR]  WITH CHECK ADD  CONSTRAINT [fk9_CAR_SituacaoPagamentoCar] FOREIGN KEY([situacaoPagamento_id])
REFERENCES [dbo].[f_SituacaoPagamentoCar] ([id])
GO

ALTER TABLE [dbo].[f_CAR] CHECK CONSTRAINT [fk9_CAR_SituacaoPagamentoCar]
GO


