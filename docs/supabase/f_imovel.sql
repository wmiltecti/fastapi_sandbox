USE [ambiental_hom]
GO

/****** Object:  Table [dbo].[f_imovel]    Script Date: 27/10/2025 09:56:34 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[f_imovel](
	[pkimovel] [int] IDENTITY(1,1) NOT NULL,
	[nome] [varchar](150) NULL,
	[areatotal] [float] NULL,
	[numero] [varchar](25) NULL,
	[livro] [varchar](15) NULL,
	[folha] [varchar](15) NULL,
	[cartorio] [varchar](50) NULL,
	[tipo] [int] NULL,
	[fkmunicipio] [int] NULL,
	[nirf] [varchar](25) NULL,
	[cidade] [varchar](50) NULL,
	[provincia] [varchar](50) NULL,
	[fkpais] [int] NULL,
	[fkestado] [int] NULL,
	[inscricaoMunicipal] [varchar](25) NULL,
	[ccirincra] [varchar](25) NULL,
	[tipoCartorio] [int] NULL,
	[fkcomarca] [int] NULL,
	[fkramoatividade] [int] NULL,
	[shapefileshp] [varchar](250) NULL,
	[shapefiledbf] [varchar](250) NULL,
	[fkprojecao] [int] NULL,
	[shapefileshx] [varchar](250) NULL,
	[certificacaoIncra] [varchar](64) NULL,
	[areaReservaLegal] [float] NULL,
	[areaPreservacaoPermanente] [float] NULL,
	[asinds] [float] NULL,
	[roteiroAcesso] [varchar](800) NULL,
	[outrosDadosPosse] [text] NULL,
	[cep] [varchar](9) NULL,
	[complemento] [varchar](800) NULL,
	[endereco] [varchar](800) NULL,
	[shapeFilePRJ] [varchar](255) NULL,
	[areaTotalAnteriorMarco] [float] NULL,
	[areaTotalCalculada] [float] NULL,
	[nomeAssentamento] [varchar](800) NULL,
	[numeroLotesAssentamento] [int] NULL,
	[tamanhoModuloFiscal] [float] NULL,
	[terrasIndigenas] [varchar](250) NULL,
	[areaTotalDiferenteAnteriorMarco] [tinyint] NULL,
	[loteReformaAgraria] [tinyint] NULL,
	[destinacaoServicoPublico] [tinyint] NULL,
	[quantidadeModuloFiscal] [float] NULL,
	[quantidadeModuloFiscalAnteriorMarco] [float] NULL,
	[fracaoIdealMediaImovel] [float] NULL,
	[orgaoAssentamento_id] [int] NULL,
	[periodoReservaLegal_id] [int] NULL,
	[possuiCar] [tinyint] NULL,
	[antecessor_id] [int] NULL,
	[dataCriacaoAssentamento] [datetime] NULL,
	[codigoProjetoAssentamento] [varchar](64) NULL,
	[versao] [int] NULL,
	[arquivoGeorreferenciamento] [varchar](250) NULL,
	[projecaoGeorreferenciamento_id] [int] NULL,
	[areaTotalApp] [float] NULL,
 CONSTRAINT [f_imovel_pkey] PRIMARY KEY CLUSTERED 
(
	[pkimovel] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

ALTER TABLE [dbo].[f_imovel]  WITH CHECK ADD  CONSTRAINT [f_Imovel_antecessor_id] FOREIGN KEY([antecessor_id])
REFERENCES [dbo].[f_imovel] ([pkimovel])
GO

ALTER TABLE [dbo].[f_imovel] CHECK CONSTRAINT [f_Imovel_antecessor_id]
GO

ALTER TABLE [dbo].[f_imovel]  WITH CHECK ADD  CONSTRAINT [f_Imovel_fkmunicipio] FOREIGN KEY([fkmunicipio])
REFERENCES [dbo].[f_municipio] ([pkmunicipio])
GO

ALTER TABLE [dbo].[f_imovel] CHECK CONSTRAINT [f_Imovel_fkmunicipio]
GO

ALTER TABLE [dbo].[f_imovel]  WITH CHECK ADD  CONSTRAINT [FK_f_Imovel_fkestado] FOREIGN KEY([fkestado])
REFERENCES [dbo].[f_estado] ([pkestado])
GO

ALTER TABLE [dbo].[f_imovel] CHECK CONSTRAINT [FK_f_Imovel_fkestado]
GO

ALTER TABLE [dbo].[f_imovel]  WITH CHECK ADD  CONSTRAINT [FK_f_Imovel_fkpais] FOREIGN KEY([fkpais])
REFERENCES [dbo].[f_pais] ([pkpais])
GO

ALTER TABLE [dbo].[f_imovel] CHECK CONSTRAINT [FK_f_Imovel_fkpais]
GO

ALTER TABLE [dbo].[f_imovel]  WITH CHECK ADD  CONSTRAINT [FK_f_Imovel_fkprojecao] FOREIGN KEY([fkprojecao])
REFERENCES [dbo].[f_projecao] ([pkprojecao])
GO

ALTER TABLE [dbo].[f_imovel] CHECK CONSTRAINT [FK_f_Imovel_fkprojecao]
GO

ALTER TABLE [dbo].[f_imovel]  WITH CHECK ADD  CONSTRAINT [fk1_Imovel_Imovel] FOREIGN KEY([antecessor_id])
REFERENCES [dbo].[f_imovel] ([pkimovel])
GO

ALTER TABLE [dbo].[f_imovel] CHECK CONSTRAINT [fk1_Imovel_Imovel]
GO

ALTER TABLE [dbo].[f_imovel]  WITH CHECK ADD  CONSTRAINT [fk2_Imovel_Estado] FOREIGN KEY([fkestado])
REFERENCES [dbo].[f_estado] ([pkestado])
GO

ALTER TABLE [dbo].[f_imovel] CHECK CONSTRAINT [fk2_Imovel_Estado]
GO

ALTER TABLE [dbo].[f_imovel]  WITH CHECK ADD  CONSTRAINT [fk3_Imovel_Municipio] FOREIGN KEY([fkmunicipio])
REFERENCES [dbo].[f_municipio] ([pkmunicipio])
GO

ALTER TABLE [dbo].[f_imovel] CHECK CONSTRAINT [fk3_Imovel_Municipio]
GO

ALTER TABLE [dbo].[f_imovel]  WITH CHECK ADD  CONSTRAINT [fk4_Imovel_Orgao] FOREIGN KEY([orgaoAssentamento_id])
REFERENCES [dbo].[f_Orgao] ([pkOrgao])
GO

ALTER TABLE [dbo].[f_imovel] CHECK CONSTRAINT [fk4_Imovel_Orgao]
GO

ALTER TABLE [dbo].[f_imovel]  WITH CHECK ADD  CONSTRAINT [fk5_Imovel_Pais] FOREIGN KEY([fkpais])
REFERENCES [dbo].[f_pais] ([pkpais])
GO

ALTER TABLE [dbo].[f_imovel] CHECK CONSTRAINT [fk5_Imovel_Pais]
GO

ALTER TABLE [dbo].[f_imovel]  WITH CHECK ADD  CONSTRAINT [fk6_Imovel_PeriodoReservaLegal] FOREIGN KEY([periodoReservaLegal_id])
REFERENCES [dbo].[f_PeriodoReservaLegal] ([id])
GO

ALTER TABLE [dbo].[f_imovel] CHECK CONSTRAINT [fk6_Imovel_PeriodoReservaLegal]
GO

ALTER TABLE [dbo].[f_imovel]  WITH CHECK ADD  CONSTRAINT [fk7_Imovel_Projecao] FOREIGN KEY([fkprojecao])
REFERENCES [dbo].[f_projecao] ([pkprojecao])
GO

ALTER TABLE [dbo].[f_imovel] CHECK CONSTRAINT [fk7_Imovel_Projecao]
GO

ALTER TABLE [dbo].[f_imovel]  WITH CHECK ADD  CONSTRAINT [fk8_Imovel_TipoImovel] FOREIGN KEY([tipo])
REFERENCES [dbo].[f_TipoImovel] ([id])
GO

ALTER TABLE [dbo].[f_imovel] CHECK CONSTRAINT [fk8_Imovel_TipoImovel]
GO

ALTER TABLE [dbo].[f_imovel]  WITH CHECK ADD  CONSTRAINT [fk9_Imovel_Projecao] FOREIGN KEY([projecaoGeorreferenciamento_id])
REFERENCES [dbo].[f_projecao] ([pkprojecao])
GO

ALTER TABLE [dbo].[f_imovel] CHECK CONSTRAINT [fk9_Imovel_Projecao]
GO

ALTER TABLE [dbo].[f_imovel]  WITH CHECK ADD  CONSTRAINT [fmvelrgoAssentamentoid] FOREIGN KEY([orgaoAssentamento_id])
REFERENCES [dbo].[f_Orgao] ([pkOrgao])
GO

ALTER TABLE [dbo].[f_imovel] CHECK CONSTRAINT [fmvelrgoAssentamentoid]
GO

ALTER TABLE [dbo].[f_imovel]  WITH CHECK ADD  CONSTRAINT [fmvlprjcGrrfrncmentoid] FOREIGN KEY([projecaoGeorreferenciamento_id])
REFERENCES [dbo].[f_projecao] ([pkprojecao])
GO

ALTER TABLE [dbo].[f_imovel] CHECK CONSTRAINT [fmvlprjcGrrfrncmentoid]
GO


