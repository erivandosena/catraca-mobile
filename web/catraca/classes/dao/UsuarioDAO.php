<?php
class UsuarioDAO extends DAO {
	/**
	 * Vamos verificar dois bancos. 
	 * Primeiro no Banco Local. Se ele n�o existir olhamos no SIG. 
	 * Se existir no SIG copiamos para o local com n�vel Default. 
	 * @param Usuario $usuario
	 * @return boolean
	 */
	public function autentica(Usuario $usuario) {
		
		/*
		 * Primeiro vou verificar no banco local . 
		 * Deu certo?
		 * Define nivel na session e deixa o cara logado. 
		 * 
		 */
		
		
		$login = $usuario->getLogin ();
		$senha = md5 ( $usuario->getSenha () );
		$sql = "SELECT * FROM usuario WHERE usua_login ='$login' AND usua_senha = '$senha' LIMIT 1";
		
		foreach ( $this->getConexao ()->query ( $sql ) as $linha ) {
			$usuario->setLogin ( $linha ['usua_login'] );
			$usuario->setId ( $linha ['usua_id'] );
			$usuario->setNivelAcesso ( $linha ['usua_nivel'] );
			return true;
		}
		//N�o deu. 
		//Vou verificar na base do SIG. 
		$daoSistemasComum = new DAO(null, DAO::TIPO_PG_SISTEMAS_COMUM);
		$result2 = 	$daoSistemasComum->getConexao()->query("SELECT * FROM vw_usuarios_autenticacao_catraca WHERE login ='$login' AND senha = '$senha' LIMIT 1");
		foreach($result2 as $linha){
			
			//Se eu to procurando aqui � pq houve algo errado no banco local. 
			//2 n�o tinha. -- nesse caso fazemos um insert. 
			//Vamos verificar isso agora. 
			//Existe esse login?
			
			//1 Minha senha est� desatualizada no local. -- Nesse caso fazemos update na senha e tentamos autenticar de novo com o Nivel que tenho.
			$result3 = $this->getConexao()->query("SELECT * FROM usuario WHERE usua_login = '$login' LIMIT 1");
			foreach($result3 as $outraLinha){
				//Vamos atualizar sua senha, meu filho. 
				$this->getConexao()->query("UPDATE usuario set usua_senha = '$senha' WHERE usua_login = '$login'");
				//Caso isso aconteceu, podemos logar de novo. Mesmo augoritimo de antes.  Fa�amos recursividade? N�o, � meio arriscado, Vamos repetir mesmo. 
				foreach ( $this->getConexao ()->query ( $sql ) as $linha2 ) {
					$usuario->setLogin ( $linha2 ['usua_login'] );
					$usuario->setId ( $linha2 ['usua_id'] );
					$usuario->setNivelAcesso ( $linha2 ['usua_nivel'] );
					return true;
				}
				
			}
			//Vish, o cara n�o existia na base local. O que faremos? 
			//Num tem pobrema! Nois adiciona! N�is rai farr� um incerte. 		
			$nivel = Sessao::NIVEL_COMUM;
			$nome = $linha['nome'];
			$email = $linha['email'];
			$idBaseExterna = $linha['id_usuario'];
			$this->getConexao()->query("INSERT into usuario(usua_login,usua_senha, usua_nome,usua_email, usua_nivel, id_base_externa) 
										VALUES				('$login', '$senha', '$nome','$email', $nivel, $idBaseExterna)");
			$usuario->setNivelAcesso ( $nivel);
			return true;
			
		}
		 
		
		
		return false;
	}
	
	/**
	 * Pesquisaremos primeiro o Login do usuario e depois o nome do laboratorio.
	 * Apos isso pegaremos o Id de cada um e usaremos numa operacao de insert.
	 * Mas essa operacao so pode funcionar se ela ainda nao existir com esse usuario e laboratorio.
	 * Terminando tudo iremos atualizar o nivel do usuario
	 * 
	 * @param Usuario $usuario        	
	 * @param Laboratorio $laboratorio        	
	 */
	public function tornarAdministrador(Usuario $usuario, Laboratorio $laboratorio) {
		$login = $usuario->getLogin();
		$nomeLaboratorio = $laboratorio->getNome();
		
		
		$sqlLaboratorio = "SELECT * FROM laboratorio WHERE nome_laboratorio = $nomeLaboratorio";
		
		
		
	}
	public function preenchePorLogin(Usuario $usuario){
		$login = $usuario->getLogin();
		$sql = "SELECT * FROM usuario WHERE login = '$login'";
		$flag = false;
		foreach($this->getConexao()->query($sql) as $linha){
			$usuario->setId($linha['id_usuario']);
			$flag = true;
			return $flag;
		}
		return $flag;
		
		
	}
	public function preenchePorNome(Laboratorio $laboratorio){
		$nome = $laboratorio->getNome();
		$sql = "SELECT * FROM laboratorio WHERE nome_laboratorio = '$nome'";
		foreach($this->getConexao()->query($sql) as $linha){
			$laboratorio->setId($linha['id_laboratorio']);
			return true;
		}
		return false;
	}
	public function ehAdministrador(Usuario $usuario, Laboratorio $laboratorio){
		$idUsuario = $usuario->getId();
		$idLaboratorio = $laboratorio->getId();
		$sql= "SELECT * FROM administrador WHERE id_usuario = $idUsuario AND id_laboratorio = $idLaboratorio";
		$result =$this->getConexao()->query($sql);
		foreach($result as $linha){
			return true;
		}
		return false;
	}
	public function adicionaAdministrador(Usuario $usuario, Laboratorio $laboratorio){
		$novoNivel = Sessao::NIVEL_ADMIN;
		$idUsuario = $usuario->getId();
		$idLaboratorio = $laboratorio->getId();
		
		$sqlUpdate = "UPDATE usuario set nivel_acesso = $novoNivel WHERE id_usuario = $idUsuario";
		$sqlInsert = "INSERT into administrador (id_usuario, id_laboratorio) VALUES($idUsuario, $idLaboratorio)";
		$this->getConexao()->beginTransaction();
		if($this->getConexao()->query($sqlUpdate)){
			if($this->getConexao()->query($sqlInsert)){
				$this->getConexao()->commit();
				return true;
			}
		}
		$this->getConexao()->rollBack();
		return false;
		
	}
	
}

?>